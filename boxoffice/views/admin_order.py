from flask import jsonify, url_for

from coaster.views import ReturnRenderWith, load_models, render_with

from .. import app, lastuser
from ..models import (
    CurrencySymbol,
    InvoiceStatus,
    ItemCollection,
    LineItem,
    LineItemStatus,
    Order,
    OrderStatus,
    Organization,
)
from .utils import check_api_access, json_date_format, xhr_only


def format_assignee(assignee):
    if assignee:
        return {
            'id': assignee.id,
            'fullname': assignee.fullname,
            'email': assignee.email,
            'phone': assignee.phone,
            'details': assignee.details,
        }
    return None


def format_line_items(line_items):
    line_item_dicts = []
    for line_item in line_items:
        line_item_dicts.append(
            {
                'title': line_item.ticket.title,
                'seq': line_item.line_item_seq,
                'id': line_item.id,
                'category': line_item.ticket.category.title,
                'description': line_item.ticket.description.text,
                'description_html': line_item.ticket.description.html,
                'currency': CurrencySymbol.INR,
                'base_amount': line_item.base_amount,
                'discounted_amount': line_item.discounted_amount,
                'final_amount': line_item.final_amount,
                'discount_policy': line_item.discount_policy.title
                if line_item.discount_policy
                else "",
                'discount_coupon': line_item.discount_coupon.code
                if line_item.discount_coupon
                else "",
                'cancelled_at': json_date_format(line_item.cancelled_at)
                if line_item.cancelled_at
                else "",
                'assignee_details': format_assignee(line_item.current_assignee),
                'cancel_ticket_url': url_for(
                    'cancel_line_item', line_item_id=line_item.id
                )
                if line_item.is_cancellable()
                else "",
            }
        )
    return line_item_dicts


def jsonify_admin_orders(data_dict):
    menu_id = data_dict['menu'].id
    order_dicts = []
    for order in data_dict['orders']:
        if order.is_confirmed:
            order_dicts.append(
                {
                    'receipt_no': order.receipt_no,
                    'id': order.id,
                    'order_date': json_date_format(order.paid_at),
                    'buyer_fullname': order.buyer_fullname,
                    'buyer_email': order.buyer_email,
                    'buyer_phone': order.buyer_phone,
                    'currency': CurrencySymbol.INR,
                    'amount': order.net_amount,
                    'url': '/menu/' + str(menu_id) + '/' + str(order.id),
                    'receipt_url': url_for('receipt', access_token=order.access_token),
                    'assignee_url': url_for(
                        'order_ticket', access_token=order.access_token
                    ),
                }
            )
    return jsonify(
        account_name=data_dict['menu'].organization.name,
        account_title=data_dict['menu'].organization.title,
        menu_title=data_dict['menu'].title,
        orders=order_dicts,
    )


@app.route('/admin/menu/<menu_id>/orders')
@lastuser.requires_login
@render_with(
    {'text/html': 'index.html.jinja2', 'application/json': jsonify_admin_orders}
)
@load_models((ItemCollection, {'id': 'menu_id'}, 'menu'), permission='org_admin')
def admin_orders(menu: ItemCollection) -> ReturnRenderWith:
    return {
        'title': menu.title,
        'menu': menu,
        'orders': menu.orders,
    }


@app.route('/admin/order/<order_id>')
@lastuser.requires_login
@xhr_only
@load_models((Order, {'id': 'order_id'}, 'order'), permission='org_admin')
def admin_order(order: Order):
    line_items = LineItem.query.filter(
        LineItem.order == order,
        LineItem.status.in_(
            [LineItemStatus.CONFIRMED.value, LineItemStatus.CANCELLED.value]
        ),
    ).all()
    return jsonify(line_items=format_line_items(line_items))


def jsonify_order(order_dict):
    org = {"title": order_dict['org'].title, "name": order_dict['org'].name}
    order = {
        'id': order_dict['order'].id,
        'buyer_fullname': order_dict['order'].buyer_fullname,
        'buyer_email': order_dict['order'].buyer_email,
        'buyer_phone': order_dict['order'].buyer_phone,
        'receipt_no': order_dict['order'].receipt_no,
        'receipt_url': url_for(
            'receipt', access_token=order_dict['order'].access_token
        ),
        'assignee_url': url_for(
            'order_ticket', access_token=order_dict['order'].access_token
        ),
    }
    menu = {'id': order_dict['order'].menu_id}
    return jsonify(
        org=org,
        menu=menu,
        order=order,
        line_items=format_line_items(order_dict['line_items']),
    )


@app.route('/admin/o/<org_name>/order/<int:receipt_no>', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (Organization, {'name': 'org_name'}, 'org'),
    (Order, {'organization': 'org', 'receipt_no': 'receipt_no'}, 'order'),
    permission='org_admin',
)
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_order})
def admin_org_order(org: Organization, order: Order) -> ReturnRenderWith:
    line_items = LineItem.query.filter(
        LineItem.order == order,
        LineItem.status.in_(
            [LineItemStatus.CONFIRMED.value, LineItemStatus.CANCELLED.value]
        ),
    ).all()
    return {'org': org, 'order': order, 'line_items': line_items}


def get_order_details(order):
    line_items_list = [
        {
            'title': li.ticket.title,
            'category': li.ticket.category.title,
            'event_date': li.ticket.event_date.isoformat()
            if li.ticket.event_date
            else None,
            'status': LineItemStatus(li.status).name,
            'base_amount': li.base_amount,
            'discounted_amount': li.discounted_amount,
            'final_amount': li.final_amount,
            'assignee': format_assignee(li.current_assignee),
            'place_of_supply_city': li.ticket.place_supply_state_code
            if li.ticket.place_supply_state_code
            else li.ticket.menu.place_supply_state_code,
            'place_of_supply_country': li.ticket.place_supply_country_code
            if li.ticket.place_supply_country_code
            else li.ticket.menu.place_supply_country_code,
            'tax_type': li.ticket.menu.tax_type,
        }
        for li in order.confirmed_and_cancelled_line_items
    ]

    invoices_list = [
        {
            'status': InvoiceStatus(invoice.status).name,
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
        }
        for invoice in order.invoices
    ]

    refunds_list = [
        {
            'refund_amount': refund.amount,
            'refund_description': refund.refund_description,
            'internal_note': refund.internal_note,
        }
        for refund in order.refund_transactions
    ]

    return jsonify(
        order_id=order.id,
        receipt_no=order.receipt_no,
        status=OrderStatus(order.status).name,
        final_amount=order.net_amount,
        line_items=line_items_list,
        title=order.menu.title,
        invoices=invoices_list,
        refunds=refunds_list,
        buyer_name=order.buyer_fullname,
        buyer_email=order.buyer_email,
        buyer_phone=order.buyer_phone,
    )


# This endpoint has been added to fetch details of an order to generate invoice outside
# Boxoffice. Not to be used within the app.
@app.route('/api/1/organization/<org_name>/order/<int:receipt_no>', methods=['GET'])
@load_models(
    (Organization, {'name': 'org_name'}, 'org'),
    (Order, {'organization': 'org', 'receipt_no': 'receipt_no'}, 'order'),
)
def order_api(org: Organization, order: Order):
    check_api_access(org.details.get('access_token'))
    return get_order_details(order)


# This endpoint has been added to fetch details of an order to generate invoice outside
# Boxoffice. Not to be used within the app.
@app.route('/api/1/organization/<org_name>/order/<order_id>', methods=['GET'])
@load_models(
    (Organization, {'name': 'org_name'}, 'org'),
    (Order, {'organization': 'org', 'id': 'order_id'}, 'order'),
)
def order_id_api(org: Organization, order: Order):
    check_api_access(org.details.get('access_token'))
    return get_order_details(order)
