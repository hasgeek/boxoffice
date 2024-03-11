from datetime import date, datetime
from typing import Any

from babel.dates import format_datetime
from flask import g, jsonify, request, url_for
from flask_babel import get_locale

from baseframe import localize_timezone
from coaster.views import ReturnRenderWith, load_models, render_with

from .. import app, lastuser
from ..extapi.razorpay import get_settled_transactions
from ..models import InvoiceStatus, LineItem, Menu, Order, Organization
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
@load_models((Menu, {'id': 'menu_id'}, 'menu'), permission='org_admin')
def admin_report(menu: Menu) -> ReturnRenderWith:
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
@load_models((Menu, {'id': 'menu_id'}, 'menu'), permission='org_admin')
def tickets_report(menu: Menu):
    headers, rows = menu.fetch_all_details()
    assignee_url_index = headers.index('assignee_url')

    def row_handler(row):
        # localize datetime
        row_list = [
            (
                v
                if not isinstance(v, datetime)
                else format_datetime(
                    localize_timezone(v), format='long', locale=get_locale() or 'en'
                )
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
@load_models((Menu, {'id': 'menu_id'}, 'menu'), permission='org_admin')
def attendees_report(menu: Menu):
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
        Menu,
        {'id': 'menu_id', 'organization': 'organization'},
        'menu',
    ),
)
def orders_api(organization: Organization, menu: Menu):
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
            # 'assignee_details' is a dict already, so copy and include prefixes
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
    invoice_filter: dict[str, Any] = {}
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
        period_from = date(today.year, today.month, 1).strftime('%Y-%m-%d')
        period_to = date(today.year, today.month, today.day).strftime('%Y-%m-%d')
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


@app.route('/admin/o/<org_name>/invoices_zoho_books.csv')
@lastuser.requires_login
@load_models(
    (Organization, {'name': 'org_name'}, 'organization'), permission='org_admin'
)
def invoices_report_zb(organization: Organization):
    today = date.today()
    period_type = request.args.get('type', 'all')
    invoice_filter: dict[str, Any] = {}
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
        period_from = date(today.year, today.month, 1).strftime('%Y-%m-%d')
        period_to = date(today.year, today.month, today.day).strftime('%Y-%m-%d')
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

    headers, rows = organization.fetch_invoice_line_items(filters=invoice_filter)

    invoice_date_index = headers.index('Invoice Date')
    invoice_number_index = headers.index('Invoice Number')
    line_item_id_index = headers.index('line_item_id')
    quantity_index = headers.index('Billing Address')
    headers.insert(quantity_index, 'Quantity')
    item_name_index = quantity_index
    headers.insert(item_name_index, 'Item Name')
    quantity_index = headers.index('Quantity')

    new_rows = []
    new_rows_index: dict[str, int] = {}

    for row in rows:
        row = list(row)
        inv_date = localize_timezone(row[invoice_date_index])
        row[invoice_date_index] = inv_date.strftime('%Y-%m-%d')
        fy_base = inv_date.year - int(inv_date.month < 4)
        fy = f'{fy_base}{fy_base - 1999}'
        row[invoice_number_index] = f'{fy}{row[invoice_number_index]}'
        invoice_number = row[invoice_number_index]
        line_item = LineItem.query.get(row[line_item_id_index])
        if line_item is None:
            continue
        item_name = line_item.ticket.menu.title
        item_key = str(invoice_number) + '^' + item_name
        if new_rows_index.get(item_key) is None:
            row.insert(item_name_index, item_name)
            row.insert(quantity_index, 1)
            new_rows.append(row)
            new_rows_index[item_key] = len(new_rows) - 1
            current_row = row
        else:
            current_row = new_rows[new_rows_index[item_key]]
            current_row[quantity_index] += 1

    order_id_index = headers.index('Sales Order Number')
    customer_name_index = headers.index('Customer Name')
    first_name_index = headers.index('Email')
    headers.insert(first_name_index, 'First Name')
    last_name_index = headers.index('Email')
    headers.insert(last_name_index, 'Last Name')
    invoicee_company_index = headers.index('invoicee_company')
    headers.pop(invoicee_company_index)
    state_index = headers.index('Billing State')
    country_index = headers.index('Billing Country')
    email_index = headers.index('Email')
    gst_treatment_index = headers.index('GST Identification Number (GSTIN)')
    gst_index = headers.index('GST Identification Number (GSTIN)')
    headers.insert(gst_treatment_index, 'GST Treatment')
    headers.pop()
    headers.append('Invoice Currency')

    def row_handler(row):
        order = Order.query.filter(Order.id == row[order_id_index]).first()
        if row[customer_name_index] is None:
            row[customer_name_index] = order.buyer_fullname
        fullname = row[customer_name_index].split(' ')
        last_name = ''
        gst_treatment = 'consumer'
        if len(fullname) > 1:
            last_name = fullname.pop()
        row.insert(first_name_index, ' '.join(fullname))
        row.insert(last_name_index, last_name)
        company_name = row.pop(invoicee_company_index)
        if company_name is not None:
            row[customer_name_index] = company_name
            if row[gst_index] is not None:
                gst_treatment = 'business_gst'
            else:
                gst_treatment = 'business_none'
        if row[state_index] is None:
            row[state_index] = 'KA'
        if row[country_index] is None:
            row[country_index] = 'IN'
        if row[country_index] != 'IN':
            gst_treatment = 'overseas'
        if row[email_index] is None:
            row[email_index] = order.buyer_email
        row.insert(gst_treatment_index, gst_treatment)
        row.pop()
        row.append(row[headers.index('Currency Code')])
        dict_row = dict(list(zip(headers, row)))
        for enum_member in InvoiceStatus:
            if dict_row.get('Invoice Status on Boxoffice') == enum_member.value:
                dict_row['Invoice Status on Boxoffice'] = enum_member.name
                break
        return dict_row

    return csv_response(headers, new_rows, row_type='dict', row_handler=row_handler)


@app.route('/admin/o/<org_name>/settlements.csv')
@lastuser.requires_permission('siteadmin')
@load_models((Organization, {'name': 'org_name'}, 'organization'))
def settled_transactions(organization: Organization):
    # FIXME: This report is NOT filtered by organization; it has everything!
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
