from flask import make_response, render_template, jsonify, request, url_for
from coaster.views import load_models, render_with
from boxoffice import app, lastuser
from boxoffice.models import ItemCollection, Order, Organization, Price, LineItem, LINE_ITEM_STATUS, ORDER_STATUS
from utils import xhr_only, cors, invoice_date_filter


def jsonify_item(item):
    price = item.current_price()
    if price:
        return {
            'name': item.name,
            'title': item.title,
            'id': item.id,
            'description': item.description.text,
            'quantity_available': item.quantity_available,
            'quantity_total': item.quantity_total,
            'category_id': item.category_id,
            'item_collection_id': item.item_collection_id,
            'price': price.amount,
            'price_category': price.title,
            'price_valid_upto': price.end_at,
            'discount_policies': [{'id': policy.id, 'title': policy.title, 'is_automatic': policy.is_automatic}
                                  for policy in item.discount_policies]
        }


def jsonify_category(category):
    category_items = []
    for item in category.items:
        item_json = jsonify_item(item)
        if item_json:
            category_items.append(item_json)
    if category_items:
        return {
            'id': category.id,
            'title': category.title,
            'name': category.name,
            'item_collection_id': category.item_collection_id,
            'items': category_items
        }

def jsonify_price(price):
    return {
        'title': price.title,
        'start_at': price.start_at,
        'end_at': price.end_at,
        'amount': price.amount,
        'currency': price.currency
    }


def jsonify_item_details(item):
    prices = Price.query.filter_by(item=item)
    prices_json = []
    if prices:
        for price in prices:
            prices_json.append(jsonify_price(price))
    discount_policies = []
    if item.discount_policies:
        discount_policies = [{'id': policy.id, 'title': policy.title, 'is_automatic': policy.is_automatic}
                              for policy in item.discount_policies]
    return {
        'id': item.id,
        'name': item.name,
        'title': item.title,
        'category': item.category.title,
        'description': item.description.text,
        'quantity_total': item.quantity_total,
        'quantity_available': item.quantity_available,
        'current_price': jsonify_item(item),
        'prices': prices_json,
        'discount_policies': discount_policies
    }


def jsonify_all_category(category):
    category_items = []
    if category.items:
        for item in category.items:
            category_items.append(jsonify_item_details(item))
    return {
        'id': category.id,
        'name': category.name,
        'title': category.title,
        'seq': category.seq,
        'items': category_items
    }

def jsonify_item_collection(item_collection):
    categories_json = []
    if item_collection.categories:
        for category in item_collection.categories:
            category_json = jsonify_all_category(category)
            categories_json.append(category_json)
    return {
        'id': item_collection.id,
        'name': item_collection.name,
        'title': item_collection.title,
        'description_text': item_collection.description_text,
        'description_html': item_collection.description_html,
        'categories': categories_json
    }

def jsonify_dashboard(data):
    item_collection = data['item_collection']
    item_collection_details = jsonify_item_collection(item_collection)
    started = [ORDER_STATUS.PURCHASE_ORDER]
    sold = [ORDER_STATUS.SALES_ORDER, ORDER_STATUS.INVOICE]
    cancelled = [ORDER_STATUS.CANCELLED]
    item_stats = {}
    for item in item_collection.items:
        #Group items based on category
        if item.category.title not in item_stats:
            item_stats[item.category.title] = []
        total_items = item.quantity_total
        sold_line_items = LineItem.query.join(Order).filter(LineItem.item == item, Order.status.in_(sold), LineItem.status==LINE_ITEM_STATUS.CONFIRMED).count()
        cancelled_line_items = LineItem.query.filter(LineItem.item == item, LineItem.status==LINE_ITEM_STATUS.CANCELLED).count()
        item_stats[item.category.title].append({'title': item.title, 'total': total_items, 'sold': sold_line_items, 'cancelled': cancelled_line_items})
    dashboard = {
        'item_collection': item_collection_details, 
        'item_stats': item_stats
    }
    return jsonify(title=item_collection.title, dashboard=dashboard, view=data['view'])

def jsonify_items(data):
    item_collection = data['item_collection']
    item_collection_details = jsonify_item_collection(item_collection)
    return jsonify(title=item_collection.title, items=item_collection_details, view=data['view'])   

def jsonify_all_orders(data):
    item_collection = data['item_collection']
    orders_json = []
    orders = data['orders']
    orders.sort(key=lambda order: order.initiated_at, reverse=True)
    for order in orders:
        all_line_items = []
        for line_item in order.line_items:
            all_line_items.append({
                'title': line_item.item.title,
                'assignee': line_item.current_assignee.fullname if line_item.current_assignee else "",
                'discount_policy': line_item.discount_policy.title if line_item.discount_policy else "",
                'discount_coupon': line_item.discount_coupon.code if line_item.discount_coupon else ""
            })
        orders_json.append({
            'invoice_no': order.invoice_no,
            'order_date': invoice_date_filter(order.paid_at, '%d %b %Y %H:%M:%S') if order.paid_at else invoice_date_filter(order.initiated_at, '%d %b %Y %H:%M:%S'),
            'status': 'Complete' if order.status else 'Incomplete',
            'buyer_fullname': order.buyer_fullname,
            'buyer_email': order.buyer_email,
            'buyer_phone': order.buyer_phone,
            'tickets': len(order.line_items),
            'total': order.get_amounts(),
            'line_items': all_line_items,
            'assignee_details': url_for('line_items', access_token=order.access_token)
        })
    return jsonify(title=item_collection.title, orders=orders_json, view=data['view'])


def jsonify_all_assignees(data):
    item_collection = data['item_collection']
    orders_json = []
    orders = data['orders']
    assignees_json = {}
    for order in orders:
        # Group line_items based on line_item.item since details will be vary for different items
        for line_item in order.line_items:
            if line_item.current_assignee:
                if line_item.item.title not in assignees_json:
                    assignees_json[line_item.item.title] = []
                assignees_json[line_item.item.title].append({
                    'invoice_no': order.invoice_no,
                    'title': line_item.item.title,
                    'fullname': line_item.current_assignee.fullname,
                    'email': line_item.current_assignee.email,
                    'phone': line_item.current_assignee.phone,
                    'details': line_item.current_assignee.details,
                    'discount_policy': line_item.discount_policy.title if line_item.discount_policy else "",
                    'discount_coupon': line_item.discount_coupon.code if line_item.discount_coupon else ""
                })
    return jsonify(title=item_collection.title, assignees=assignees_json, view=data['view'])


@app.route('/api/1/boxoffice.js')
@cors
def boxofficejs():
    return make_response(jsonify({
        'script': render_template('boxoffice.js', base_url=request.url_root.strip('/'),
        razorpay_key_id=app.config['RAZORPAY_KEY_ID'])
    }))


@app.route('/ic/<item_collection>', methods=['GET', 'OPTIONS'])
@load_models(
    (ItemCollection, {'id': 'item_collection'}, 'item_collection')
    )
@xhr_only
@cors
def item_collection(item_collection):
    categories_json = []
    item_collection.categories.sort(key=lambda category: category.seq)
    for category in item_collection.categories:
        category_json = jsonify_category(category)
        if category_json:
            categories_json.append(category_json)
    return jsonify(html=render_template('boxoffice.html'), categories=categories_json)


@app.route('/<organization>/item_collection/new', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (Organization, {'name': 'organization'}, 'organization'),
    )
@xhr_only
def add_item_collection(organization):
    # Add new item collection and send all item collections in org
    return make_response(jsonify(message="Item collection add"), 201)


@app.route('/<organization>/<item_collection>', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with({'text/html': 'item_collection.html', 'application/json': jsonify_dashboard}, json=True)
@load_models(
    (Organization, {'name': 'organization'}, 'organization'),
    (ItemCollection, {'name': 'item_collection'}, 'item_collection')
    )
def view_item_collection(organization, item_collection):
    return dict(org=organization, item_collection=item_collection, view='dashboard')


@app.route('/<organization>/<item_collection>/edit', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (ItemCollection, {'id': 'item_collection'}, 'item_collection')
    )
@xhr_only
def update_item_collection(item_collection):
    # Update and send all item collections in org
    return make_response(jsonify(message="Item collection updated"), 201)


@app.route('/<organization>/<item_collection>/delete', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (ItemCollection, {'id': 'item_collection'}, 'item_collection')
    )
@xhr_only
def delete_item_collection(item_collection):
    # Delete item_collection
    return make_response(jsonify(message="Item collection deleted"), 201)


@app.route('/<organization>/<item_collection>/items', methods=['GET'])
@lastuser.requires_login
@load_models(
    (Organization, {'name': 'organization'}, 'organization'),
    (ItemCollection, {'name': 'item_collection'}, 'item_collection')
    )
@render_with({'text/html': 'item_collection.html', 'application/json': jsonify_items}, json=True)
def all_items(organization, item_collection):
    return dict(org=organization, item_collection=item_collection, view='items')


@app.route('/<organization>/<item_collection>/orders', methods=['GET'])
@lastuser.requires_login
@load_models(
    (Organization, {'name': 'organization'}, 'organization'),
    (ItemCollection, {'name': 'item_collection'}, 'item_collection')
    )
@render_with({'text/html': 'item_collection.html', 'application/json': jsonify_all_orders}, json=True)
def all_order(organization, item_collection):
    orders = Order.query.filter_by(item_collection=item_collection).all()
    return dict(org=organization, item_collection=item_collection, orders=orders, view='orders')


@app.route('/<organization>/<item_collection>/assignees', methods=['GET'])
@lastuser.requires_login
@load_models(
    (Organization, {'name': 'organization'}, 'organization'),
    (ItemCollection, {'name': 'item_collection'}, 'item_collection')
    )
@render_with({'text/html': 'item_collection.html', 'application/json': jsonify_all_assignees}, json=True)
def all_assignees(organization, item_collection):
    orders = Order.query.filter_by(item_collection=item_collection, status=ORDER_STATUS.SALES_ORDER).all()
    return dict(org=organization, item_collection=item_collection, orders=orders, view='assignees')
