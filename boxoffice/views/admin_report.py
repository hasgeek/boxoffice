# -*- coding: utf-8 -*-

from flask import Response
from .. import app, lastuser
from coaster.views import load_models
from boxoffice.models import db, ItemCollection, Order, Item, LineItem, Assignee, LINE_ITEM_STATUS


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

    def generate():
        for row in records:
            yield ','.join([unicode(attr) for attr in row]) + '\n'
    return Response(generate(), mimetype='text/csv')
