# -*- coding: utf-8 -*-

import datetime
from flask import jsonify, g, request
from decimal import Decimal
from .. import app, lastuser
from coaster.views import load_models, render_with
from baseframe import localize_timezone, _
from baseframe.forms import render_form
from boxoffice.models import db, Organization, ItemCollection
from boxoffice.models.line_item import sales_delta, sales_by_date, counts_per_date_per_item
from boxoffice.forms import ItemCollectionForm
from boxoffice.views.utils import api_error, api_success
from boxoffice.views.admin_item import format_item_details


def jsonify_item_collection(item_collection_dict):
    return jsonify(org_name=item_collection_dict['item_collection'].organization.name,
        org_title=item_collection_dict['item_collection'].organization.title,
        ic_name=item_collection_dict['item_collection'].name,
        ic_title=item_collection_dict['item_collection'].title,
        categories=[{'title': category.title, 'id': category.id, 'items': [format_item_details(item) for item in category.items]}
            for category in item_collection_dict['item_collection'].categories],
        date_item_counts=item_collection_dict['date_item_counts'],
        date_sales=item_collection_dict['date_sales'],
        today_sales=item_collection_dict['today_sales'],
        net_sales=item_collection_dict['item_collection'].net_sales,
        sales_delta=item_collection_dict['sales_delta']
    )


@app.route('/admin/ic/<ic_id>')
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_item_collection})
@load_models(
    (ItemCollection, {'id': 'ic_id'}, 'item_collection'),
    permission='org_admin'
)
def admin_item_collection(item_collection):
    item_ids = [str(item.id) for item in item_collection.items]
    date_item_counts = {}
    date_sales = {}
    for sales_date, sales_count in counts_per_date_per_item(item_collection, g.user.timezone).items():
        date_sales[sales_date.isoformat()] = sales_by_date(sales_date, item_ids, g.user.timezone)
        date_item_counts[sales_date.isoformat()] = sales_count
    today_sales = date_sales.get(localize_timezone(datetime.datetime.utcnow(), g.user.timezone).date().isoformat(), Decimal(0))
    return dict(title=item_collection.title, item_collection=item_collection, date_item_counts=date_item_counts,
        date_sales=date_sales, today_sales=today_sales,
        sales_delta=sales_delta(g.user.timezone, item_ids))


def jsonify_new_item_collection(item_collection_dict):
    ic_form = ItemCollectionForm()
    if request.method == 'GET':
        return jsonify(form_template=render_form(form=ic_form,
            title=u"New item collection", submit=u"Create", ajax=False, with_chrome=False))
    if ic_form.validate_on_submit():
        ic = ItemCollection(organization=item_collection_dict['organization'])
        ic_form.populate_obj(ic)
        if not ic.name:
            ic.make_name()
        db.session.add(ic)
        db.session.commit()
        return api_success(result={'item_collection': dict(ic.current_access())},
            doc=_(u"New item collection created"), status_code=201)
    return api_error(message=_(u"There was a problem with creating the item collection"),
        errors=ic_form.errors, status_code=400)


@app.route('/admin/o/<org>/ic/new', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_new_item_collection})
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    permission='org_admin'
)
def admin_new_ic(organization):
    return dict(organization=organization)


def jsonify_edit_item_collection(item_collection_dict):
    item_collection = item_collection_dict['item_collection']
    ic_form = ItemCollectionForm(obj=item_collection)
    if request.method == 'GET':
        return jsonify(form_template=render_form(form=ic_form,
            title=u"Edit item collection", submit=u"Save", ajax=False, with_chrome=False))
    if ic_form.validate_on_submit():
        ic_form.populate_obj(item_collection)
        db.session.commit()
        return api_success(result={'item_collection': dict(item_collection.current_access())},
            doc=_(u"Edited item collection {title}.".format(title=item_collection.title)), status_code=200)
    return api_error(message=_(u"There was a problem with editing the item collection"),
        errors=ic_form.errors, status_code=400)


@app.route('/admin/ic/<ic_id>/edit', methods=['POST', 'GET'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_edit_item_collection})
@load_models(
    (ItemCollection, {'id': 'ic_id'}, 'item_collection'),
    permission='org_admin'
)
def admin_edit_ic(item_collection):
    return dict(item_collection=item_collection)
