# -*- coding: utf-8 -*-

from flask import Response, jsonify
from .. import app, lastuser
from coaster.views import load_models, render_with
from boxoffice.models import db, ItemCollection, Order, Item, LineItem, Assignee, DiscountPolicy, LINE_ITEM_STATUS
from boxoffice.views.utils import csv_response


def jsonify_report(data_dict):
    return jsonify(org_name=data_dict['item_collection'].organization.name, title=data_dict['item_collection'].title)


@app.route('/admin/ic/<id>/reports')
@lastuser.requires_login
@load_models(
    (ItemCollection, {'id': 'id'}, 'item_collection'),
    permission='org_admin')
@render_with({'text/html': 'index.html', 'application/json': jsonify_report})
def admin_report(item_collection):
    return dict(title=item_collection.organization.title, item_collection=item_collection)


@app.route('/admin/ic/<id>/reports/tickets.csv')
@lastuser.requires_login
@load_models(
    (ItemCollection, {'id': 'id'}, 'item_collection'),
    permission='org_admin')
def admin_line_items_report(item_collection):
    line_item_join = db.outerjoin(LineItem, Assignee).outerjoin(DiscountPolicy).join(Item).join(Order)
    line_item_query = db.select([LineItem.id, Item.title, LineItem.base_amount, LineItem.discounted_amount, LineItem.final_amount, DiscountPolicy.title, Order.buyer_fullname, Order.buyer_email, Order.buyer_phone, Assignee.fullname, Assignee.email, Assignee.phone, Assignee.details]).select_from(line_item_join).where(LineItem.status == LINE_ITEM_STATUS.CONFIRMED).where(Assignee.current == True).where(Order.item_collection == item_collection).order_by('created_at')
    rows = db.session.execute(line_item_query).fetchall()
    headers = ['ticket id', 'item title', 'base amount', 'discounted amount', 'final amount', 'discount policy', 'buyer fullname', 'buyer email', 'buyer phone', 'attendee fullname', 'attendee email', 'attendee phone', 'attendee details']

    return csv_response(headers, rows)
