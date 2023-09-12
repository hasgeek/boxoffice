from datetime import date, datetime

from babel.dates import format_datetime
from flask import g, jsonify, request, url_for
from flask_babel import get_locale

from baseframe import localize_timezone
from coaster.views import ReturnRenderWith, load_models, render_with

from .. import app, lastuser
from ..extapi.razorpay import get_settled_transactions
from ..models import InvoiceStatus, ItemCollection, Order, Organization
from .utils import api_error, check_api_access, csv_response


def jsonify_report(data_dict):
    return jsonify(
        account_name=data_dict['menu'].organization.name,
        account_title=data_dict['menu'].organization.title,
        menu_name=data_dict['menu'].name,
        menu_title=data_dict['menu'].title,
    )


@app.route('/admin/menu/<menu_id>/reports')
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_report})
@load_models((ItemCollection, {'id': 'menu_id'}, 'menu'), permission='org_admin')
def admin_report(menu: ItemCollection) -> ReturnRenderWith:
    return {'menu': menu}


def jsonify_org_report(data_dict):
    return jsonify(account_title=data_dict['organization'].title)


@app.route('/admin/o/<org_name>/reports')
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_org_report})
@load_models(
    (Organization, {'name': 'org_name'}, 'organization'), permission='org_admin'
)
def admin_org_report(organization: Organization) -> ReturnRenderWith:
    return {'organization': organization}


@app.route('/admin/menu/<menu_id>/tickets.csv')
@lastuser.requires_login
@load_models((ItemCollection, {'id': 'menu_id'}, 'menu'), permission='org_admin')
def tickets_report(menu: ItemCollection):
    headers, rows = menu.fetch_all_details()
    assignee_url_index = headers.index('assignee_url')

    def row_handler(row):
        # localize datetime
        row_list = [
            v
            if not isinstance(v, datetime)
            else format_datetime(
                localize_timezone(v), format='long', locale=get_locale() or 'en'
            )
            for v in row
        ]
        # add assignee url
        access_token = row_list[assignee_url_index]
        if access_token:
            row_list[assignee_url_index] = url_for(
                'order_ticket', access_token=access_token, _external=True
            )
        return row_list

    return csv_response(headers, rows, row_handler=row_handler)


@app.route('/admin/menu/<menu_id>/attendees.csv')
@lastuser.requires_login
@load_models((ItemCollection, {'id': 'menu_id'}, 'menu'), permission='org_admin')
def attendees_report(menu: ItemCollection):
    # Generated a unique list of headers for all 'assignee_details' keys in all items in
    # this menu. This flattens the 'assignee_details' dict. This will need to
    # be updated if we add additional dicts to our csv export.
    attendee_details_headers = []
    for ticket in menu.tickets:
        if ticket.assignee_details:
            for detail in ticket.assignee_details.keys():
                attendee_detail_prefixed = 'attendee_details_' + detail
                # Eliminate duplicate headers across attendee_details across items. For
                # example, if 't-shirt' and 'hoodie' are two items with a 'size' key,
                # you only want one column in the csv called size.
                if attendee_detail_prefixed not in attendee_details_headers:
                    attendee_details_headers.append(attendee_detail_prefixed)

    headers, rows = menu.fetch_assignee_details()
    headers.extend(attendee_details_headers)

    if 'attendee_details' in headers:
        attendee_details_index = headers.index('attendee_details')
    else:
        attendee_details_index = -1

    def row_handler(row):
        # Convert row to a dict
        dict_row = {}
        for idx, item in enumerate(row):
            # 'assignee_details' is a dict already, so copy and include prefixes
            if idx == attendee_details_index and isinstance(item, dict):
                for key in item.keys():
                    dict_row['attendee_details_' + key] = item[key]
            # Item is a datetime object, so format and add to dict
            elif isinstance(item, datetime):
                dict_row[headers[idx]] = format_datetime(
                    localize_timezone(item), format='long', locale=get_locale() or 'en'
                )
            # Item is a string, add it to the dict with the corresponding key
            else:
                dict_row[headers[idx]] = item
        return dict_row

    csv_headers = list(headers)
    # Remove 'attendee_details' from header
    if 'attendee_details' in headers:
        csv_headers.remove('attendee_details')

    return csv_response(csv_headers, rows, row_type='dict', row_handler=row_handler)


@app.route('/api/1/organization/<org>/menu/<menu_id>/orders.csv')
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    (
        ItemCollection,
        {'id': 'menu_id', 'organization': 'organization'},
        'menu',
    ),
)
def orders_api(organization: Organization, menu: ItemCollection):
    check_api_access(organization.details.get('access_token'))

    # Generated a unique list of headers for all 'assignee_details' keys in all items in
    # this menu. This flattens the 'assignee_details' dict. This will need to
    # be updated if we add additional dicts to our csv export.
    attendee_details_headers = []
    for ticket in menu.tickets:
        if ticket.assignee_details:
            for detail in ticket.assignee_details.keys():
                attendee_detail_prefixed = 'attendee_details_' + detail
                # Eliminate duplicate headers across attendee_details across tickets.
                # For example, if 't-shirt' and 'hoodie' are two tickets with a 'size'
                # key, you only want one column in the csv called size.
                if attendee_detail_prefixed not in attendee_details_headers:
                    attendee_details_headers.append(attendee_detail_prefixed)
    headers, rows = menu.fetch_all_details()
    headers.extend(attendee_details_headers)

    if 'attendee_details' in headers:
        attendee_details_index = headers.index('attendee_details')
    else:
        attendee_details_index = -1

    def row_handler(row):
        # Convert row to a dict
        dict_row = {}
        for idx, item in enumerate(row):
            # 'assignee_details' is a dict already, so copy and include prefixs
            if idx == attendee_details_index and isinstance(item, dict):
                for key in item.keys():
                    dict_row['attendee_details_' + key] = item[key]
            # Item is a datetime object, so format and add to dict
            elif isinstance(item, datetime):
                dict_row[headers[idx]] = format_datetime(
                    localize_timezone(item), format='long', locale=get_locale() or 'en'
                )
            # Value is a string, add it to the dict with the corresponding key
            else:
                dict_row[headers[idx]] = item
        return dict_row

    csv_headers = list(headers)
    # Remove 'attendee_details' from header
    if 'attendee_details' in headers:
        csv_headers.remove('attendee_details')

    return csv_response(csv_headers, rows, row_type='dict', row_handler=row_handler)


@app.route('/admin/o/<org_name>/invoices.csv')
@lastuser.requires_login
@load_models(
    (Organization, {'name': 'org_name'}, 'organization'), permission='org_admin'
)
def invoices_report(organization: Organization):
    today = date.today()
    period_type = request.args.get('type', 'all')
    invoice_filter = {}
    if period_type == 'monthly':
        period_month = request.args.get('month', None)
        if period_month is not None:
            [year, month] = [int(d) for d in period_month.split('-')]
            try:
                date(year, month, 1)
            except (ValueError, TypeError):
                return api_error(
                    message='Invalid year/month',
                    status_code=403,
                    errors=['invalid_month'],
                )
        else:
            year_rollback = date.month == 1
            [year, month] = [
                today.year - int(year_rollback),
                today.month - 1 if not year_rollback else 12,
            ]
        invoice_filter['year'] = year
        invoice_filter['month'] = month
    elif period_type == 'custom':
        period_from = date(today.year, today.month, 1)
        period_to = date(today.year, today.month, today.day)
        period_from = request.args.get('from', period_from)
        try:
            invoice_filter['from'] = datetime.strptime(period_from, '%Y-%m-%d')
        except (ValueError, TypeError):
            return api_error(
                message='Invalid from date',
                status_code=403,
                errors=['invalid_from_date'],
            )
        period_to = request.args.get('to', period_to)
        try:
            invoice_filter['to'] = datetime.strptime(period_to, '%Y-%m-%d')
        except (ValueError, TypeError):
            return api_error(
                message='Invalid to date', status_code=403, errors=['invalid_to_date']
            )

    headers, rows = organization.fetch_invoices(filters=invoice_filter)
    order_id_index = headers.index('order_id')
    buyer_name_index = headers.index('buyer_taxid')
    headers.insert(buyer_name_index, 'buyer_name')
    buyer_email_index = headers.index('buyer_taxid')
    headers.insert(buyer_email_index, 'buyer_email')

    def row_handler(row):
        order = Order.query.filter(Order.id == row[order_id_index]).first()
        row = list(row)
        row.insert(buyer_name_index, order.buyer_fullname)
        row.insert(buyer_email_index, order.buyer_email)
        dict_row = dict(list(zip(headers, row)))
        for enum_member in InvoiceStatus:
            if dict_row.get('status') == enum_member.value:
                dict_row['status'] = enum_member.name
                break
        if isinstance(dict_row.get('invoiced_at'), datetime):
            dict_row['invoiced_at'] = format_datetime(
                localize_timezone(dict_row['invoiced_at']),
                format='long',
                locale=get_locale() or 'en',
            )
        return dict_row

    return csv_response(headers, rows, row_type='dict', row_handler=row_handler)


@app.route('/admin/o/<org_name>/settlements.csv')
@load_models((Organization, {'name': 'org_name'}, 'organization'))
def settled_transactions(organization: Organization):
    today = date.today()
    year = int(request.args.get('year', today.year))
    month = int(request.args.get('month', today.month))
    try:
        date(year, month, 1)
    except (ValueError, TypeError):
        return api_error(
            message='Invalid year/month', status_code=403, errors=['invalid_date']
        )
    headers, rows = get_settled_transactions(
        {'year': year, 'month': month}, g.user.timezone
    )
    return csv_response(headers, rows, row_type='dict')
