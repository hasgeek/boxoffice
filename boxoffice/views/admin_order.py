# -*- coding: utf-8 -*-

from flask import jsonify, url_for
from .. import app, lastuser
from coaster.views import load_models, render_with
from ..models import ItemCollection, Organization, Order, CURRENCY_SYMBOL, LineItem, LINE_ITEM_STATUS, ORDER_STATUS, INVOICE_STATUS
from .utils import json_date_format, xhr_only, check_api_access


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
                'url': '/ic/' + str(item_collection_id) + '/' + str(order.id),
                'receipt_url': url_for('receipt', access_token=order.access_token),
                'assignee_url': url_for('line_items', access_token=order.access_token)
                })
    return jsonify(org_name=data_dict['item_collection'].organization.name,
        org_title=data_dict['item_collection'].organization.title,
        ic_title=data_dict['item_collection'].title, orders=order_dicts)


@app.route('/admin/ic/<ic_id>/orders')
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_admin_orders})
@load_models(
    (ItemCollection, {'id': 'ic_id'}, 'item_collection'),
    permission='org_admin'
    )
def admin_orders(item_collection):
    return dict(title=item_collection.title, item_collection=item_collection, orders=item_collection.orders)


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


def jsonify_order(order_dict):
    org = {
        "title": order_dict['org'].title,
        "name": order_dict['org'].name
        }
    order = {
        "id": order_dict['order'].id,
        "buyer_fullname": order_dict['order'].buyer_fullname,
        "buyer_email": order_dict['order'].buyer_email,
        "buyer_phone": order_dict['order'].buyer_phone,
        "invoice_no": order_dict['order'].invoice_no,
        "receipt_url": url_for('receipt', access_token=order_dict['order'].access_token),
        "assignee_url": url_for('line_items', access_token=order_dict['order'].access_token)
        }
    ic = {
        'id': order_dict['order'].item_collection_id
        }
    return jsonify(
        org=org,
        ic=ic,
        order=order,
        line_items=format_line_items(order_dict['line_items'])
        )


@app.route('/admin/o/<org_name>/order/<int:receipt_no>', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (Organization, {'name': 'org_name'}, 'org'),
    (Order, {'organization': 'org', 'receipt_no': 'receipt_no'}, 'order'),
    permission='org_admin'
    )
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_order})
def admin_org_order(org, order):
    line_items = LineItem.query.filter(LineItem.order == order,
        LineItem.status.in_([LINE_ITEM_STATUS.CONFIRMED, LINE_ITEM_STATUS.CANCELLED])).all()
    return dict(org=org, order=order, line_items=line_items)


def get_order_details(order):
    line_items_list = [{
        'title': li.item.title,
        'category': li.item.category.title,
        'event_date': li.item.event_date.isoformat() if li.item.event_date else None,
        'status': LINE_ITEM_STATUS[li.status],
        'base_amount': li.base_amount,
        'discounted_amount': li.discounted_amount,
        'final_amount': li.final_amount,
        'assignee': format_assignee(li.current_assignee),
        'place_of_supply_city': li.item.place_supply_state_code if li.item.place_supply_state_code else li.item.item_collection.place_supply_state_code,
        'place_of_supply_country': li.item.place_supply_country_code if li.item.place_supply_country_code else li.item.item_collection.place_supply_country_code,
        'tax_type': li.item.item_collection.tax_type
        } for li in order.confirmed_and_cancelled_line_items]

    invoices_list = [{
        'status': INVOICE_STATUS[invoice.status],
        'invoicee_name': invoice.invoicee_name,
        'invoicee_company': invoice.invoicee_company,
        'invoicee_email': invoice.invoicee_email,
        'invoice_no': invoice.invoice_no,
        'invoiced_at': invoice.invoiced_at,
        'street_address_1': invoice.street_address_1,
        'street_address_2': invoice.street_address_2,
        'city': invoice.city,
        'state': invoice.state,
        'state_code': invoice.state_code,
        'country_code': invoice.country_code,
        'postcode': invoice.postcode,
        'buyer_taxid': invoice.buyer_taxid,
        'seller_taxid': invoice.seller_taxid,
        } for invoice in order.invoices]

    refunds_list = [{
        'refund_amount': refund.amount,
        'refund_description': refund.refund_description,
        'internal_note': refund.internal_note
        } for refund in order.refund_transactions]

    return jsonify(
        order_id=order.id,
        receipt_no=order.receipt_no,
        status=ORDER_STATUS[order.status],
        final_amount=order.net_amount,
        line_items=line_items_list,
        title=order.item_collection.title,
        invoices=invoices_list,
        refunds=refunds_list,
        buyer_name=order.buyer_fullname,
        buyer_email=order.buyer_email,
        buyer_phone=order.buyer_phone
        )


# This endpoint has been added to fetch details of an order to generate invoice outside Boxoffice.
# Not to be used within the app.
@app.route('/api/1/organization/<org_name>/order/<int:receipt_no>', methods=['GET'])
@load_models(
    (Organization, {'name': 'org_name'}, 'org'),
    (Order, {'organization': 'org', 'receipt_no': 'receipt_no'}, 'order')
    )
def order_api(org, order):
    check_api_access(org.details.get('access_token'))
    return get_order_details(order)


# This endpoint has been added to fetch details of an order to generate invoice outside Boxoffice.
# Not to be used within the app.
@app.route('/api/1/organization/<org_name>/order/<order_id>', methods=['GET'])
@load_models(
    (Organization, {'name': 'org_name'}, 'org'),
    (Order, {'organization': 'org', 'id': 'order_id'}, 'order')
    )
def order_id_api(org, order):
    check_api_access(org.details.get('access_token'))
    return get_order_details(order)
