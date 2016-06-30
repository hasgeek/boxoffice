# -*- coding: utf-8 -*-

import datetime
from flask import jsonify, g, url_for
from decimal import Decimal
from .. import app, lastuser
from sqlalchemy import func
from coaster.views import load_models, render_with
from boxoffice.models import db, ItemCollection, Order, LineItem, LINE_ITEM_STATUS, CURRENCY_SYMBOL
from boxoffice.models.line_item import sales_delta, sales_by_date, counts_per_date_per_item
from boxoffice.views.order import jsonify_assignee
from utils import invoice_date_filter


def jsonify_item(item):
    sold = LineItem.query.filter(LineItem.item == item, LineItem.final_amount > 0, LineItem.status == LINE_ITEM_STATUS.CONFIRMED).count()
    free = LineItem.query.filter(LineItem.item == item, LineItem.final_amount == 0, LineItem.status == LINE_ITEM_STATUS.CONFIRMED).count()
    cancelled = LineItem.query.filter(LineItem.item == item, LineItem.status == LINE_ITEM_STATUS.CANCELLED).count()
    net_sales = db.session.query(func.sum(LineItem.final_amount)).filter(LineItem.item == item, LineItem.status == LINE_ITEM_STATUS.CONFIRMED).first()
    return {
        'id': item.id,
        'title': item.title,
        'available': item.quantity_available,
        'sold': sold,
        'free': free,
        'cancelled': cancelled,
        'current_price': item.current_price().amount if item.current_price() else "No active price",
        'net_sales': net_sales[0] if net_sales[0] else 0
    }


def jsonify_item_collection(item_collection_dict):
    item_ids = [item.id for item in item_collection_dict['item_collection'].items]
    net_sales = db.session.query(func.sum(LineItem.final_amount)).filter(LineItem.item_id.in_(item_ids), LineItem.status == LINE_ITEM_STATUS.CONFIRMED).first()
    return jsonify(title=item_collection_dict['item_collection'].title,
        items=[jsonify_item(item) for item in item_collection_dict['item_collection'].items],
        date_item_counts=item_collection_dict['date_item_counts'],
        date_sales=item_collection_dict['date_sales'],
        today_sales=item_collection_dict['today_sales'],
        net_sales=net_sales[0] if net_sales[0] else 0,
        sales_delta=item_collection_dict['sales_delta'])


def jsonify_admin_orders(data_dict):
    title = data_dict['item_collection'].title
    ic_id = data_dict['item_collection'].id
    orders_json = []
    orders = data_dict['orders']
    orders.sort(key=lambda order: order.initiated_at, reverse=True)
    for order in orders:
        orders_json.append({
            'invoice_no': order.invoice_no,
            'id': order.id,
            'order_date': invoice_date_filter(order.paid_at, '%d %b %Y %H:%M:%S') if order.paid_at else invoice_date_filter(order.initiated_at, '%d %b %Y %H:%M:%S'),
            'status': 'Complete' if order.status else 'Incomplete',
            'buyer_fullname': order.buyer_fullname,
            'buyer_email': order.buyer_email,
            'buyer_phone': order.buyer_phone,
            'currency': CURRENCY_SYMBOL['INR'],
            'amount': order.get_amounts().final_amount,
            'url': url_for('admin_order', ic_id=ic_id, order_id=order.id)
        })
    return jsonify(title=title, orders=orders_json)


def jsonify_admin_order(order_dict):
    title = order_dict['title']
    order = order_dict['order']
    all_line_items = []
    order_json = []
    for line_item in order.line_items:
        item = {
            'title': line_item.item.title,
            'category': line_item.item.category.title,
            'description': line_item.item.description.text,
            'currency': CURRENCY_SYMBOL['INR'],
            'base_amount': line_item.base_amount,
            'discounted_amount': line_item.discounted_amount,
            'final_amount': line_item.final_amount,
            'discount_policy': line_item.discount_policy.title if line_item.discount_policy else "",
            'discount_coupon': line_item.discount_coupon.code if line_item.discount_coupon else "",
            'cancelled_at': line_item.cancelled_at,
            'assignee_details': jsonify_assignee(line_item.current_assignee)
        }
        all_line_items.append(item)
    all_line_items.sort(key=lambda category_seq: category_seq)
    order_json.append({
        'invoice_no': order.invoice_no,
        'id': order.id,
        'order_date': invoice_date_filter(order.paid_at, '%d %b %Y %H:%M:%S') if order.paid_at else invoice_date_filter(order.initiated_at, '%d %b %Y %H:%M:%S'),
        'status': 'Complete' if order.status else 'Incomplete',
        'buyer_fullname': order.buyer_fullname,
        'buyer_email': order.buyer_email,
        'buyer_phone': order.buyer_phone,
        'tickets': len(order.line_items),
        'currency': CURRENCY_SYMBOL['INR'],
        'amount': order.get_amounts().final_amount,
        'line_items': all_line_items,
        'receipt': url_for('receipt', access_token=order.access_token),
        'assignee': url_for('line_items', access_token=order.access_token)
    })
    return jsonify(title=title, order=order_json)


@app.route('/admin/ic/<ic_id>')
@lastuser.requires_login
@load_models(
    (ItemCollection, {'id': 'ic_id'}, 'item_collection'),
    permission='org_admin'
    )
@render_with({'text/html': 'index.html', 'application/json': jsonify_item_collection}, json=True)
def admin_item_collection(item_collection):
    item_ids = [str(item.id) for item in item_collection.items]
    date_item_counts = counts_per_date_per_item(item_collection, g.user.timezone)
    date_sales = sales_by_date(date_item_counts.keys(), g.user.timezone, item_ids)
    today_sales = date_sales.get(datetime.datetime.now().strftime("%Y-%m-%d"), Decimal(0))
    return dict(item_collection=item_collection, date_item_counts=date_item_counts,
        date_sales=date_sales, today_sales=today_sales,
        sales_delta=sales_delta(g.user.timezone, item_ids))


@app.route('/admin/ic/<ic_id>/orders')
@lastuser.requires_login
@load_models(
    (ItemCollection, {'id': 'ic_id'}, 'item_collection'),
    permission='org_admin'
    )
@render_with({'text/html': 'index.html', 'application/json': jsonify_admin_orders}, json=True)
def admin_all_order(item_collection):
    orders = Order.query.filter_by(item_collection=item_collection).all()
    return dict(item_collection=item_collection, orders=orders)


@app.route('/admin/ic/<ic_id>/<order_id>')
@lastuser.requires_login
@load_models(
    (ItemCollection, {'id': 'ic_id'}, 'item_collection'),
    (Order, {'id': 'order_id'}, 'order'),
    permission='org_admin'
    )
@render_with({'text/html': 'index.html', 'application/json': jsonify_admin_order}, json=True)
def admin_order(item_collection, order):
    order = Order.query.filter_by(item_collection=item_collection, id=order.id).first()
    return dict(title=item_collection.title, order=order)
