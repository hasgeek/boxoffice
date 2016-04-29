from flask import make_response, render_template, jsonify, request
from coaster.views import load_models, render_with
from boxoffice import app, lastuser
from boxoffice.models import Organization, ItemCollection
from utils import xhr_only, cors


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


def jsonify_item_collection(data):
    item_collection = data['item_collection']
    categories_json = []
    if item_collection.categories:
        for category in item_collection.categories:
            category_json = jsonify_all_category(category)
            categories_json.append(category_json)
    item_collection_details = {
        'id': item_collection.id,
        'name': item_collection.name,
        'title': item_collection.title,
        'description_text': item_collection.description_text,
        'description_html': item_collection.description_html,
        'categories': categories_json
    }
    return jsonify(item_collection=item_collection_details)


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
@render_with({'text/html': 'item_collection.html', 'application/json': jsonify_item_collection}, json=True)
@load_models(
    (Organization, {'name': 'organization'}, 'organization'),
    (ItemCollection, {'name': 'item_collection'}, 'item_collection')
    )
def view_item_collection(organization, item_collection):
    return dict(org=organization, item_collection=item_collection)


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
