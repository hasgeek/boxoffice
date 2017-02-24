# -*- coding: utf-8 -*-

from flask import jsonify, url_for
from .. import app, lastuser
from coaster.views import load_models, render_with
from boxoffice.models import ItemCollection, Order, CURRENCY_SYMBOL, LineItem, LINE_ITEM_STATUS
from utils import date_time_format, xhr_only


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
            'cancelled_at': date_time_format(line_item.cancelled_at) if line_item.cancelled_at else "",
            'assignee_details': format_assignee(line_item.current_assignee),
            'cancel_ticket_url': url_for('cancel_line_item', line_item_id=line_item.id) if line_item.is_cancellable() else ""
        })
    return line_item_dicts


def jsonify_admin_orders(data_dict):
    item_collection_id = data_dict['item_collection'].id
    order_dicts = []
    for order in data_dict['orders']:
        if (order.is_confirmed):
            order_dicts.append({
                'invoice_no': order.invoice_no,
                'id': order.id,
                'order_date': date_time_format(order.paid_at),
                'buyer_fullname': order.buyer_fullname,
                'buyer_email': order.buyer_email,
                'buyer_phone': order.buyer_phone,
                'currency': CURRENCY_SYMBOL['INR'],
                'amount': order.get_amounts(LINE_ITEM_STATUS.CONFIRMED).confirmed_amount,
                'url': '/ic/' + unicode(item_collection_id) + '/' + unicode(order.id),
                'receipt': url_for('receipt', access_token=order.access_token),
                'assignee': url_for('line_items', access_token=order.access_token)
            })
    return jsonify(org_name=data_dict['item_collection'].organization.name, title=data_dict['item_collection'].title, orders=order_dicts)


@app.route('/api/1/admin/ic/<ic_id>/orders')
@lastuser.requires_login
@load_models(
    (ItemCollection, {'id': 'ic_id'}, 'item_collection'),
    permission='org_admin'
    )
@render_with({'text/html': 'index.html', 'application/json': jsonify_admin_orders}, json=True)
def admin_orders(item_collection):
    return dict(title=item_collection.organization.title, item_collection=item_collection, orders=item_collection.orders)


@app.route('/api/1/admin/ic/<ic_id>/orders/<order_id>')
@lastuser.requires_login
@load_models(
    (Order, {'id': 'order_id'}, 'order'),
    permission='org_admin'
    )
@xhr_only
def admin_order(order):
    line_items = LineItem.query.filter(LineItem.order == order, LineItem.status.in_([LINE_ITEM_STATUS.CONFIRMED, LINE_ITEM_STATUS.CANCELLED])).all()
    return jsonify(line_items=format_line_items(line_items))
