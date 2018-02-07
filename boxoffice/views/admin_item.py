# -*- coding: utf-8 -*-

from flask import g, jsonify, request
from .. import app, lastuser
from coaster.utils import buid
from coaster.views import load_models, requestargs, render_with
from baseframe import _
from baseframe.forms import render_form
from boxoffice.models import db, Organization, ItemCollection, Item, Price
from boxoffice.views.utils import api_error, api_success
from boxoffice.forms import PriceForm
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
            ItemCollection.organization == organization).filter(
            Item.title.ilike('%{query}%'.format(query=search))).join(Item.item_collection).options(
            db.Load(Item).load_only('id', 'title'),
            db.Load(ItemCollection).load_only('id', 'title')).all()
        return api_success(result={'items': [{
            'id': str(item_tuple[0].id),
            'title': "{ic_title}: {title}".format(ic_title=item_tuple[1].title, title=item_tuple[0].title)
        } for item_tuple in filtered_items]}, doc="Filtered items", status_code=200)
    else:
        return api_error(message=_(u"Missing search query"), status_code=400)


def jsonify_item(data_dict):
    discount_policies_list = []
    for policy in data_dict['item'].discount_policies:
        details = dict(policy.access_for(user=g.user))
        if policy.is_price_based:
            dp_price = Price.query.filter(Price.discount_policy == policy).first()
            details['price_details'] = {'amount': dp_price.amount}
        discount_policies_list.append(details)
    return jsonify(org_name=data_dict['item'].item_collection.organization.name,
        org_title=data_dict['item'].item_collection.organization.title,
        ic_name=data_dict['item'].item_collection.name,
        ic_title=data_dict['item'].item_collection.title,
        item=dict(data_dict['item'].access_for(user=g.user)),
        prices=[dict(price.access_for(user=g.user)) for price in data_dict['item'].prices],
        discount_policies=discount_policies_list,
        price_form=render_form(form=PriceForm(), title=u"New Price", submit=u"Save", ajax=False, with_chrome=False))


@app.route('/admin/item/<item_id>', methods=['GET'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_item})
@load_models(
    (Item, {'id': 'item_id'}, 'item'),
    permission='org_admin'
    )
def admin_item(item):
    data_dict = {}
    data_dict['item'] = item
    return dict(title=item.title, item=item)


@app.route('/admin/item/<item_id>/price/new', methods=['POST'])
@lastuser.requires_login
@xhr_only
@load_models(
    (Item, {'id': 'item_id'}, 'item'),
    permission='org_admin'
    )
def admin_new_price(item):
    price_form = PriceForm()
    if price_form.validate_on_submit():
        price = Price(item=item)
        price_form.populate_obj(price)
        price.title = item.title + '-price-' + buid()
        if not price.name:
            price.make_name()
        db.session.add(price)
        db.session.commit()
        return api_success(result={'price': dict(price.access_for(user=g.user))}, doc=_(u"New price created"), status_code=201)
    return api_error(message=_(u"There was a problem with creating the price"), errors=price_form.errors, status_code=400)


@app.route('/admin/price/<price_id>/edit', methods=['POST', 'GET'])
@lastuser.requires_login
@load_models(
    (Price, {'id': 'price_id'}, 'price'),
    permission='org_admin'
    )
def admin_price(price):
    price_form = PriceForm(obj=price)
    if request.method == 'GET':
        return jsonify(form_template=render_form(form=price_form, title=u"Edit Price", submit=u"Save", ajax=False, with_chrome=False))
    if price_form.validate_on_submit():
        price_form.populate_obj(price)
        db.session.commit()
        return api_success(result={'price_form': dict(price_form.access_for(user=g.user))}, doc=_(u"Edited price {title}.".format(title=price.title)), status_code=200)
    return api_error(message=_(u"There was a problem with editing the price"), errors=price_form.errors, status_code=400)
