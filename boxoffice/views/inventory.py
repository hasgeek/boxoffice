from pytz import utc, timezone
from boxoffice import app
from flask import redirect, url_for, render_template, request
from coaster.views import load_models, jsonp

from boxoffice.models import Organization, Item, Category, Inventory, Price

#U3_JesHfQ2OUmdihAXaAGQ


def item_json(item):
    price = Price.current(item)
    if price:
        return {
            'title': item.title,
            'id': item.id,
            'description': item.description,
            'quantity_available': item.quantity_available,
            'quantity_total': item.quantity_total,
            'category_id': item.category_id,
            'inventory_id': item.inventory_id,
            'price': Price.current(item).amount
        }


def category_json(category, items):
    return {
        'id': category.id,
        'title': category.title,
        'inventory_id': category.inventory_id,
        'items': [item_json(i) for i in items]
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
        'categories': [category_json(c, Item.query.filter_by(category=c)) for c in categories]
        })
