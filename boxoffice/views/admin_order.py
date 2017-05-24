# -*- coding: utf-8 -*-

from flask import jsonify, url_for
from .. import app, lastuser
from coaster.views import load_models, render_with, requestargs
from boxoffice.models import ItemCollection, Order, CURRENCY_SYMBOL, LineItem, LINE_ITEM_STATUS
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
    item_collection_id = data_dict['item_collection_id']
    order_dicts = []
    for order in data_dict['orders']:
        if (order.is_confirmed):
            order_dicts.append({
                'invoice_no': order.invoice_no,
                'id': order.id,
                'order_date': json_date_format(order.paid_at),
                'buyer_fullname': order.buyer_fullname,
                'buyer_email': order.buyer_email,
                'buyer_phone': order.buyer_phone,
                'currency': CURRENCY_SYMBOL['INR'],
                'amount': order.net_amount,
                'is_fully_assigned': "Filled" if order.is_fully_assigned() else "Incomplete",
                'url': '/ic/' + unicode(item_collection_id) + '/' + unicode(order.id),
                'receipt': url_for('receipt', access_token=order.access_token),
                'assignee': url_for('line_items', access_token=order.access_token)
            })
    return jsonify(org_name=data_dict['org_name'],
        title=data_dict['title'],
        orders=order_dicts,
        total_pages=data_dict['total_pages'],
        paginated=data_dict['total_pages'] > 1,
        current_page=data_dict['current_page'])


@app.route('/admin/ic/<ic_id>/orders')
@lastuser.requires_login
@render_with({'text/html': 'index.html', 'application/json': jsonify_admin_orders})
@load_models(
    (ItemCollection, {'id': 'ic_id'}, 'item_collection'),
    permission='org_admin'
    )
@requestargs('search', ('page', int), ('size', int))
def admin_orders(item_collection, search=None, page=1, size=None):
    results_per_page = size or 20

    orders = item_collection.orders
    if search:
        orders = orders.filter(
            Order.buyer_fullname.ilike('%{query}%'.format(query=search)))

    paginated_orders = orders.paginate(page=page, per_page=results_per_page)
    return dict(title=item_collection.title,
        org_name=item_collection.organization.name,
        item_collection_id=item_collection.id,
        orders=paginated_orders.items,
        total_pages=paginated_orders.pages,
        paginated=(paginated_orders.total > results_per_page),
        current_page=page)


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
