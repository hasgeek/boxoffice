# -*- coding: utf-8 -*-

from datetime import datetime
from flask import jsonify, request
from .. import app, lastuser
from coaster.views import load_models, requestargs, render_with
from baseframe import _
from baseframe.forms import render_form
from boxoffice.models import db, Organization, ItemCollection, Item, Price
from boxoffice.views.utils import api_error, api_success, json_date_format
from boxoffice.forms import ItemForm, PriceForm
from utils import xhr_only


@app.route('/admin/o/<org>/items')
@lastuser.requires_login
@xhr_only
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    permission='org_admin'
)
@requestargs('search')
def items(organization, search=None):
    if search:
        filtered_items = db.session.query(Item, ItemCollection).filter(
            ItemCollection.organization == organization, db.or_(
                Item.title.ilike('%{query}%'.format(query=search)),
                ItemCollection.title.ilike('%{query}%'.format(query=search)))).join(
            Item.item_collection).options(
                db.Load(Item).load_only('id', 'title'),
                db.Load(ItemCollection).load_only('id', 'title')).all()
        return api_success(result={'items': [{
            'id': str(item_tuple[0].id),
            'title': "{ic_title}: {title}".format(ic_title=item_tuple[1].title, title=item_tuple[0].title)
        } for item_tuple in filtered_items]}, doc="Filtered items", status_code=200)
    else:
        return api_error(message=_(u"Missing search query"), status_code=400)


def jsonify_price(price):
    price_details = dict(price.current_access())
    price_details['tense'] = price.tense()
    return price_details


def format_demand_curve(item):
    result = dict()
    demand_counter = 0

    for amount, quantity_demanded in reversed(item.demand_curve()):
        demand_counter += quantity_demanded
        result[amount] = {
            'quantity_demanded': quantity_demanded,
            'demand': demand_counter
        }
    return result


def format_item_details(item):
    item_details = dict(item.current_access())
    item_details['sold_count'] = item.sold_count()
    item_details['free_count'] = item.free_count()
    item_details['cancelled_count'] = item.cancelled_count()
    item_details['net_sales'] = item.net_sales()
    item_details['quantity_available'] = item.quantity_available
    item_details['active_price'] = item.active_price
    return item_details


def jsonify_item(data_dict):
    item = data_dict['item']
    discount_policies_list = []
    for policy in item.discount_policies:
        details = dict(policy.current_access())
        if policy.is_price_based:
            dp_price = Price.query.filter(Price.discount_policy == policy).first()
            details['price_details'] = {'amount': dp_price.amount}
        discount_policies_list.append(details)

    return jsonify(org_name=data_dict['item'].item_collection.organization.name,
        demand_curve=format_demand_curve(item),
        org_title=data_dict['item'].item_collection.organization.title,
        ic_id=data_dict['item'].item_collection.id,
        ic_name=data_dict['item'].item_collection.name,
        ic_title=data_dict['item'].item_collection.title,
        item=format_item_details(data_dict['item']),
        prices=[jsonify_price(price) for price in data_dict['item'].standard_prices()],
        discount_policies=discount_policies_list)


@app.route('/admin/item/<item_id>', methods=['GET'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_item})
@load_models(
    (Item, {'id': 'item_id'}, 'item'),
    permission='org_admin'
)
def admin_item(item):
    return dict(item=item)


def jsonify_new_item(data_dict):
    item_collection = data_dict['item_collection']
    item_form = ItemForm(parent=item_collection)
    if request.method == 'GET':
        return jsonify(form_template=render_form(form=item_form, title=u"New item", submit=u"Create", with_chrome=False))
    if item_form.validate_on_submit():
        item = Item(item_collection=item_collection)
        item_form.populate_obj(item)
        if not item.name:
            item.make_name()
        db.session.add(item)
        db.session.commit()
        return api_success(result={'item': dict(item.current_access())}, doc=_(u"New item created"), status_code=201)
    return api_error(message=_(u"There was a problem with creating the item"), errors=item_form.errors, status_code=400)


@app.route('/admin/ic/<ic_id>/item/new', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_new_item})
@load_models(
    (ItemCollection, {'id': 'ic_id'}, 'item_collection'),
    permission='org_admin'
)
def admin_new_item(item_collection):
    return dict(item_collection=item_collection)


def jsonify_edit_item(data_dict):
    item = data_dict['item']
    item_form = ItemForm(obj=item)
    if request.method == 'GET':
        return jsonify(form_template=render_form(form=item_form, title=u"Update item", submit=u"Update", with_chrome=False))
    if item_form.validate_on_submit():
        item_form.populate_obj(item)
        db.session.commit()
        return api_success(result={'item': dict(item.current_access())}, doc=_(u"Item updated"), status_code=200)
    return api_error(message=_(u"There was a problem with updating the item"), status_code=400, errors=item_form.errors)


@app.route('/admin/item/<item_id>/edit', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_edit_item})
@load_models(
    (Item, {'id': 'item_id'}, 'item'),
    permission='org_admin'
)
def admin_edit_item(item):
    return dict(item=item)


def jsonify_new_price(data_dict):
    item = data_dict['item']
    price_form = PriceForm(parent=item)
    if request.method == 'GET':
        return jsonify(form_template=render_form(form=price_form, title=u"New price", submit=u"Save", with_chrome=False))
    if price_form.validate_on_submit():
        price = Price(item=item)
        price_form.populate_obj(price)
        price.title = u"{item_name}-price-{datetime}".format(item_name=item.name,
            datetime=json_date_format(datetime.utcnow()))
        if not price.name:
            price.make_name()
        db.session.add(price)
        db.session.commit()
        return api_success(result={'price': dict(price.current_access())}, doc=_(u"New price created"), status_code=201)
    return api_error(message=_(u"There was a problem with creating the price"), status_code=400, errors=price_form.errors)


@app.route('/admin/item/<item_id>/price/new', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_new_price})
@load_models(
    (Item, {'id': 'item_id'}, 'item'),
    permission='org_admin'
)
def admin_new_price(item):
    return dict(item=item)


def jsonify_edit_price(data_dict):
    price = data_dict['price']
    price_form = PriceForm(obj=price)
    if request.method == 'GET':
        return jsonify(form_template=render_form(form=price_form, title=u"Update price", submit=u"Save", with_chrome=False))
    if price_form.validate_on_submit():
        price_form.populate_obj(price)
        db.session.commit()
        return api_success(result={'price': dict(price.current_access())}, doc=_(u"Update price {title}.".format(title=price.title)), status_code=200)
    return api_error(message=_(u"There was a problem with editing the price"), status_code=400, errors=price_form.errors)


@app.route('/admin/item/<item_id>/price/<price_id>/edit', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_edit_price})
@load_models(
    (Price, {'id': 'price_id'}, 'price'),
    permission='org_admin'
)
def admin_edit_price(price):
    return dict(price=price)
