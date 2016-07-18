# -*- coding: utf-8 -*-

from flask import jsonify, url_for
from .. import app, lastuser
from coaster.views import load_models, render_with
from boxoffice.models import ItemCollection, CURRENCY_SYMBOL, ORDER_STATUS
from utils import invoice_date_filter


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
            'cancelled_at': invoice_date_filter(line_item.cancelled_at, '%d %b %Y %H:%M:%S') if line_item.cancelled_at else "",
            'assignee_details': format_assignee(line_item.current_assignee),
            'cancel_ticket_url': url_for('cancel_line_item', line_item_id=line_item.id) if line_item.is_cancellable() else ""
        })
    return line_item_dicts


def jsonify_admin_orders(data_dict):
    item_collection_id = data_dict['item_collection'].id
    order_dicts = []
    for order in data_dict['orders']:
        order_dicts.append({
            'invoice_no': order.invoice_no,
            'id': order.id,
            'order_date': invoice_date_filter(order.paid_at, '%d %b %Y %H:%M:%S') if order.paid_at else invoice_date_filter(order.initiated_at, '%d %b %Y %H:%M:%S'),
            'status': ORDER_STATUS.get(order.status).value,
            'buyer_fullname': order.buyer_fullname,
            'buyer_email': order.buyer_email,
            'buyer_phone': order.buyer_phone,
            'currency': CURRENCY_SYMBOL['INR'],
            'amount': order.get_amounts().final_amount,
            'url': '/ic/' + unicode(item_collection_id) + '/' + unicode(order.id),
            'fully_assigned': order.is_fully_assigned() if order.is_confirmed else False,
            'receipt': url_for('receipt', access_token=order.access_token),
            'assignee': url_for('line_items', access_token=order.access_token),
            'line_items': format_line_items(order.line_items)
        })
    return jsonify(org_name=data_dict['item_collection'].organization.name, title=data_dict['item_collection'].title, orders=order_dicts)


@app.route('/admin/ic/<ic_id>/orders')
@lastuser.requires_login
@load_models(
    (ItemCollection, {'id': 'ic_id'}, 'item_collection'),
    permission='org_admin'
    )
@render_with({'text/html': 'index.html', 'application/json': jsonify_admin_orders}, json=True)
def admin_orders(item_collection):
    return dict(title=item_collection.organization.title, item_collection=item_collection, orders=item_collection.orders)
