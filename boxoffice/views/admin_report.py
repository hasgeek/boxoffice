# -*- coding: utf-8 -*-

from flask import Response, jsonify
from .. import app, lastuser
from coaster.views import load_models, render_with
from boxoffice.models import db, ItemCollection, Order, Item, LineItem, Assignee, LINE_ITEM_STATUS


def jsonify_report(data_dict):
    return jsonify(org_name=data_dict['item_collection'].organization.name, title=data_dict['item_collection'].title)


@app.route('/admin/ic/<ic_id>/reports')
@lastuser.requires_login
@load_models(
    (ItemCollection, {'id': 'ic_id'}, 'item_collection'),
    permission='org_admin'
    )
@render_with({'text/html': 'index.html', 'application/json': jsonify_report}, json=True)
def admin_report(item_collection):
    return dict(title=item_collection.organization.title, item_collection=item_collection)


@app.route('/admin/ic/<ic_id>/reports/attendee.csv')
@lastuser.requires_login
@load_models(
    (ItemCollection, {'id': 'ic_id'}, 'item_collection'),
    permission='org_admin'
    )
def admin_assignee_report(item_collection):
    line_item_join = db.outerjoin(LineItem, Assignee).join(Item).join(Order)
    line_item_stmt = db.select([LineItem.id, Item.title, Order.buyer_fullname, Order.buyer_email, Order.buyer_phone, Assignee.fullname, Assignee.email, Assignee.phone, Assignee.details]).select_from(line_item_join).where(LineItem.status == LINE_ITEM_STATUS.CONFIRMED).where(Assignee.current == True).where(Order.item_collection == item_collection).order_by('created_at')
    records = db.session.execute(line_item_stmt).fetchall()
    headers = [['line item id', 'item title', 'buyer fullname', 'buyer email', 'buyer phone', 'attendee fullname', 'attendee email', 'attendee phone', 'attendee details']]

    def generate():
        for row in headers + records:
            yield ','.join([unicode(attr) for attr in row]) + '\n'
    return Response(generate(), mimetype='text/csv')
