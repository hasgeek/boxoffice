# -*- coding: utf-8 -*-

import unicodecsv
from cStringIO import StringIO
from flask import jsonify, Response
from .. import app, lastuser
from coaster.views import load_models, render_with
from boxoffice.models import ItemCollection, Order


order_headers = [
    'id',
    'paid date',
    'invoice no',
    'final amount',
    'buyer name',
    'buyer email',
    'buyer phone',
    'item title',
    'item base amount',
    'item discounted amount',
    'item final amount',
    'item status',
    'attendee name',
    'attendee email',
    'attendee phone'
    ]


def order_data(order):
    return [
        order.id,
        order.paid_at,
        order.invoice_no,
        order.get_amounts().final_amount,
        order.buyer_fullname,
        order.buyer_email,
        order.buyer_phone]


def line_item_details(line_item, col):
    for k, v in line_item.current_assignee.details.items():
        col.append(v) if v else col.append('')
    col.append(line_item.current_assignee.details)
    return col


def line_item_data(line_item, col):
    col.extend([
        line_item.item.title,
        line_item.base_amount,
        line_item.discounted_amount,
        line_item.final_amount,
        'cancelled' if line_item.status else 'confirmed'
        ])
    if line_item.current_assignee:
        col.extend([
            line_item.current_assignee.fullname,
            line_item.current_assignee.email,
            line_item.current_assignee.phone,
            ])
        return line_item_details(line_item, col)
    else:
        return col


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


@app.route('/admin/ic/<ic_id>/reports/order')
@lastuser.requires_login
@load_models(
    (ItemCollection, {'id': 'ic_id'}, 'item_collection'),
    permission='org_admin'
    )
def admin_order_report(item_collection):
    orders = Order.query.filter_by(item_collection=item_collection).order_by('created_at').all()
    outfile = StringIO()
    out = unicodecsv.writer(outfile, encoding='utf-8')
    out.writerow(order_headers)
    for order in orders:
        if (order.is_confirmed):
            col = []
            for line_item in order.line_items:
                col = order_data(order)
                out.writerow(line_item_data(line_item, col))
    outfile.seek(0)
    contents = outfile.getvalue()
    outfile.close
    return Response(unicode(contents, 'utf-8'), mimetype='text/csv')
