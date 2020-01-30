# -*- coding: utf-8 -*-

from flask import render_template, jsonify, request, Markup
from baseframe import localized_country_list
from coaster.views import load_models
from coaster.utils import getbool
from boxoffice import app
from boxoffice.models import Organization, ItemCollection, Item, DiscountPolicy
from .utils import xhr_only, cors, sanitize_coupons
from boxoffice.data import indian_states


def jsonify_item(item):
    if item.restricted_entry:
        code_list = sanitize_coupons(request.args.getlist('code')) if 'code' in request.args else None
        if not code_list or not DiscountPolicy.is_valid_access_coupon(item, code_list):
            return None

    price = item.current_price()
    if not price:
        return None

    return {
        'name': item.name,
        'title': item.title,
        'id': item.id,
        'description': item.description.text,
        'quantity_available': item.quantity_available,
        'is_available': item.is_available,
        'quantity_total': item.quantity_total,
        'category_id': item.category_id,
        'item_collection_id': item.item_collection_id,
        'price': price.amount,
        'price_category': price.title,
        'price_valid_upto': price.end_at,
        'has_higher_price': item.has_higher_price(price),
        'discount_policies': [{'id': policy.id, 'title': policy.title, 'is_automatic': policy.is_automatic}
                              for policy in item.discount_policies]
        }


def jsonify_category(category):
    category_items = []
    for item in Item.get_by_category(category):
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


def render_boxoffice_js():
    return render_template(
        'boxoffice.js',
        base_url=request.url_root.rstrip('/'), razorpay_key_id=app.config['RAZORPAY_KEY_ID'],
        states=[{'name': state['name'], 'code': state['short_code_text']}
            for state in sorted(indian_states, key=lambda k: k['name'])],
        countries=[{'name': name, 'code': code} for code, name in localized_country_list()]
        )


@app.route('/api/1/boxoffice.js')
@cors
def boxofficejs():
    return jsonify({
        'script': render_boxoffice_js()
        })


@app.route('/ic/<item_collection>', methods=['GET', 'OPTIONS'])
@xhr_only
@cors
@load_models(
    (ItemCollection, {'id': 'item_collection'}, 'item_collection')
    )
def item_collection(item_collection):
    categories_json = []
    for category in item_collection.categories:
        category_json = jsonify_category(category)
        if category_json:
            categories_json.append(category_json)
    return jsonify(html=render_template('boxoffice.html.jinja2'), categories=categories_json, refund_policy=item_collection.organization.details.get('refund_policy', ''))


@app.route('/<org_name>/<item_collection_name>', methods=['GET', 'OPTIONS'])
@load_models(
    (Organization, {'name': 'org_name'}, 'organization'),
    (ItemCollection, {'name': 'item_collection_name', 'organization': 'organization'}, 'item_collection')
    )
def item_collection_listing(organization, item_collection):
    show_title = getbool(request.args.get('show_title', True))
    return render_template('item_collection_listing.html.jinja2',
        organization=organization,
        item_collection=item_collection,
        show_title=show_title, boxoffice_js=Markup(render_boxoffice_js()))
