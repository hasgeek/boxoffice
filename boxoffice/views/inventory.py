from flask import redirect, url_for, render_template, request
from flask.ext.cors import cross_origin
from coaster.views import load_models, jsonp
from boxoffice import app
from boxoffice.models import Organization, Item, Category, Inventory, Price

ALLOWED_ORIGINS = ['http://shreyas-wlan.dev:8000']

def item_json(item):
    price = Price.current(item)
    if price:
        return {
            'name': item.name,
            'title': item.title,
            'id': item.id,
            'description': item.description,
            'quantity_available': item.quantity_available,
            'quantity_total': item.quantity_total,
            'category_id': item.category_id,
            'inventory_id': item.inventory_id,
            'price': Price.current(item).amount
        }


def category_json(category):
    return {
        'id': category.id,
        'title': category.title,
        'inventory_id': category.inventory_id,
        'items': [item_json(item) for item in category.items]
    }


@app.route('/<organization>/<inventory>')
@load_models(
    (Organization, {'name': 'organization'}, 'organization'),
    (Inventory, {'name': 'inventory'}, 'inventory')
    )
def inventory(organization, inventory):
    items = inventory.items
    categories = inventory.categories
    return jsonp(**{
        'html': render_template('boxoffice.html'),
        'categories': [category_json(category) for category in inventory.categories]
        })

@app.route('/<organization>/<inventory>/order', methods=['POST'])
@load_models(
    (Organization, {'name': 'organization'}, 'organization'),
    (Inventory, {'name': 'inventory'}, 'inventory')
    )
@cross_origin(origins=ALLOWED_ORIGINS, methods=['GET', 'OPTIONS', 'POST'])
def order(organization, inventory):
    # change to get user
    user = User.query.first()
    order = Order(user=user, inventory=inventory)
    order.calculate(request.form.line_items)
    db.session.add(order)
    payment = Payment(pg_payment_id=request.form.pg_payment_id, order=order)
    db.session.add(payment)
    # payment.capture
    # Transaction(payment=payment)
    # return jsonify(...)
    db.session.commit()
    return jsonp(**{
        'order_id': order.id
        })
