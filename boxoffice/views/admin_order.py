# -*- coding: utf-8 -*-

from flask import jsonify, url_for
from .. import app, lastuser
from coaster.views import load_models, render_with
from boxoffice.models import ItemCollection, Order, CURRENCY_SYMBOL, LineItem, LINE_ITEM_STATUS, ORDER_STATUS
from utils import json_date_format, xhr_only


def format_assignee(assignee):
    if assignee:
        return {
            'id': assignee.id,
            'fullname': assignee.fullname,
            'email': assignee.email,
            'phone': assignee.phone,
            'details': assignee.details
        }


def format_line_items(line_items):
    line_item_dicts = []
    for line_item in line_items:
        line_item_dicts.append({
            'title': line_item.item.title,
            'seq': line_item.line_item_seq,
            'id': line_item.id,
            'category': line_item.item.category.title,
            'description': line_item.item.description.text,
            'currency': CURRENCY_SYMBOL['INR'],
            'base_amount': line_item.base_amount,
            'discounted_amount': line_item.discounted_amount,
            'final_amount': line_item.final_amount,
            'discount_policy': line_item.discount_policy.title if line_item.discount_policy else "",
            'discount_coupon': line_item.discount_coupon.code if line_item.discount_coupon else "",
            'cancelled_at': json_date_format(line_item.cancelled_at) if line_item.cancelled_at else "",
            'assignee_details': format_assignee(line_item.current_assignee),
            'cancel_ticket_url': url_for('cancel_line_item', line_item_id=line_item.id) if line_item.is_cancellable() else ""
        })
    return line_item_dicts


def jsonify_admin_orders(data_dict):
    item_collection_id = data_dict['item_collection'].id
    order_dicts = []
    orders = Order.fetch_order_transactions(item_collection_id)
    for order in orders:
        order_dicts.append({
            'id': order[0],
            'invoice_no': order[1],
            'order_date': json_date_format(order[2]),
            'buyer_fullname': order[3],
            'buyer_email': order[4],
            'buyer_phone': order[5],
            'currency': CURRENCY_SYMBOL['INR'],
            'amount': order[7],
            'url': '/ic/' + unicode(item_collection_id) + '/' + unicode(order[0]),
            'receipt': url_for('receipt', access_token=order[6]),
            'assignee': url_for('line_items', access_token=order[6])
        })
    resp = jsonify(org_name=data_dict['item_collection'].organization.name,
        org_title=data_dict['item_collection'].organization.title,
        ic_title=data_dict['item_collection'].title, orders=order_dicts)
    return resp


@app.route('/admin/ic/<ic_id>/orders')
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_admin_orders})
@load_models(
    (ItemCollection, {'id': 'ic_id'}, 'item_collection'),
    permission='org_admin'
    )
def admin_orders(item_collection):
    return dict(title=item_collection.title, item_collection=item_collection)


@app.route('/admin/order/<order_id>')
@lastuser.requires_login
@xhr_only
@load_models(
    (Order, {'id': 'order_id'}, 'order'),
    permission='org_admin'
    )
def admin_order(order):
    line_items = LineItem.query.filter(LineItem.order == order, LineItem.status.in_([LINE_ITEM_STATUS.CONFIRMED, LINE_ITEM_STATUS.CANCELLED])).all()
    return jsonify(line_items=format_line_items(line_items))
