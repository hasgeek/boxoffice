from flask import jsonify, render_template, request
from markupsafe import Markup

from baseframe import localized_country_list
from coaster.utils import getbool
from coaster.views import load_models

from .. import app
from ..data import indian_states
from ..models import (
    Category,
    CurrencySymbol,
    DiscountPolicy,
    Menu,
    Organization,
    Ticket,
)
from .utils import cors, sanitize_coupons, xhr_only


def jsonify_ticket(ticket: Ticket):
    if ticket.restricted_entry:
        code_list = (
            sanitize_coupons(request.args.getlist('code'))
            if 'code' in request.args
            else None
        )
        if not code_list or not DiscountPolicy.is_valid_access_coupon(
            ticket, code_list
        ):
            return None

    price = ticket.current_price()
    if not price:
        return None

    return {
        'name': ticket.name,
        'title': ticket.title,
        'id': ticket.id,
        'description': ticket.description.text,
        'description_html': ticket.description.html,
        'quantity_available': ticket.quantity_available,
        'is_available': ticket.is_available,
        'quantity_total': ticket.quantity_total,
        'category_id': ticket.category_id,
        'menu_id': ticket.menu_id,
        'price': price.amount,
        'price_category': price.title,
        'price_valid_upto': price.end_at,
        'has_higher_price': ticket.has_higher_price(price),
        'discount_policies': [
            {
                'id': policy.id,
                'title': policy.title,
                'is_automatic': policy.is_automatic,
                'percentage': policy.percentage,
            }
            for policy in ticket.discount_policies
        ],
    }


def jsonify_category(category: Category):
    category_items = []
    for ticket in Ticket.get_by_category(category):
        ticket_json = jsonify_ticket(ticket)
        if ticket_json:
            category_items.append(ticket_json)
    if category_items:
        return {
            'id': category.id,
            'title': category.title,
            'name': category.name,
            'menu_id': category.menu_id,
            'tickets': category_items,
        }
    return None


def render_boxoffice_js():
    return render_template(
        'boxoffice.js.jinja2',
        base_url=request.url_root.rstrip('/'),
        razorpay_key_id=app.config['RAZORPAY_KEY_ID'],
        states=[
            {'name': state['name'], 'code': state['short_code_text']}
            for state in sorted(indian_states, key=lambda k: k['name'])
        ],
        countries=[
            {'name': name, 'code': code} for code, name in localized_country_list()
        ],
    )


@app.route('/api/1/boxoffice.js')
@cors
def boxofficejs():
    return jsonify({'script': render_boxoffice_js()})


@app.route('/menu/<menu_id>', methods=['GET', 'OPTIONS'])
@xhr_only
@cors
@load_models((Menu, {'id': 'menu_id'}, 'menu'))
def view_menu(menu: Menu):
    categories_json = []
    html = render_template('boxoffice.html.jinja2')
    subscription_purchase = False
    for category in menu.categories:
        category_json = jsonify_category(category)
        if category_json:
            categories_json.append(category_json)
            if len(menu.categories) == 1 and len(category_json['tickets']) == 1:
                html = render_template('single_purchase.html.jinja2')
                subscription_purchase = True
    return jsonify(
        html=html,
        categories=categories_json,
        refund_policy=menu.organization.details.get('refund_policy', ''),
        currency=CurrencySymbol.INR,
        subscription_purchase=subscription_purchase,
    )


@app.route('/<org>/<menu_name>', methods=['GET', 'OPTIONS'])
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    (
        Menu,
        {'name': 'menu_name', 'organization': 'organization'},
        'menu',
    ),
)
def menu_listing(organization: Organization, menu: Menu):
    show_title = getbool(request.args.get('show_title', True))
    return render_template(
        'item_collection_listing.html.jinja2',
        organization=organization,
        menu=menu,
        show_title=show_title,
        boxoffice_js=Markup(render_boxoffice_js()),
    )
