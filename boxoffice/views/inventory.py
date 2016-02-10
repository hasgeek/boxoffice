from flask import render_template
from flask.ext.cors import cross_origin
from coaster.views import load_models, jsonp
from boxoffice import app
from boxoffice.models import Organization, Inventory, Price

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


@app.route('/boxoffice.js')
def boxofficejs():
    return render_template('boxoffice.js',
        base_url=app.config.get('BASE_URL'), razorpay_key_id=app.config.get('RAZORPAY_KEY_ID'))


@app.route('/<organization>/<inventory>')
@load_models(
    (Organization, {'name': 'organization'}, 'organization'),
    (Inventory, {'name': 'inventory'}, 'inventory')
    )
@cross_origin(origins=app.config.get('ALLOWED_ORIGINS'))
def inventory(organization, inventory):
    return jsonp(**{
        'html': render_template('boxoffice.html'),
        'categories': [category_json(category) for category in inventory.categories]
        })
