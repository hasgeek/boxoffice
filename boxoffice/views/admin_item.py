# -*- coding: utf-8 -*-

from flask import jsonify
from .. import app, lastuser
from coaster.views import load_models, render_with
from boxoffice.models import Item
from boxoffice.views.utils import localize


def jsonify_item(item):
    prices = [{
        'id': price.id, 'title': price.title,
        'currency': price.currency,
        'amount': price.amount,
        'start_at': localize(price.start_at, app.config['TIMEZONE']).strftime("%b %d, %Y at %I:%M %p"),
        'end_at': localize(price.end_at, app.config['TIMEZONE']).strftime("%b %d, %Y at %I:%M %p")
    } for price in item['prices']]
    discount_policies = [{
        'title': policy.title
    } for policy in item['discount_policies']]
    return jsonify(title=item['title'],
        description=item['description'],
        category_title=item['category_title'],
        prices=prices, discount_policies=discount_policies)


@app.route('/admin/item/<item_id>')
@lastuser.requires_login
@load_models(
    (Item, {'id': 'item_id'}, 'item'),
    permission='org_admin'
    )
@render_with({'text/html': 'index.html', 'application/json': jsonify_item}, json=True)
def admin_item(item):
    return dict(title=item.title, description=item.description_text,
        category_title=item.category.title, prices=item.prices,
        discount_policies=item.discount_policies.all())
