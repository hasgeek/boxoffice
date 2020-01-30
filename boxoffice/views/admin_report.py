# -*- coding: utf-8 -*-

from flask import jsonify, request, g, url_for
from .. import app, lastuser
from coaster.views import load_models, render_with
from baseframe import localize_timezone, get_locale
from boxoffice.models import Organization, ItemCollection, INVOICE_STATUS
from boxoffice.views.utils import check_api_access, csv_response, api_error
from babel.dates import format_datetime
from datetime import datetime, date
from ..extapi.razorpay import get_settled_transactions


def jsonify_report(data_dict):
    return jsonify(org_name=data_dict['item_collection'].organization.name,
        org_title=data_dict['item_collection'].organization.title,
        ic_name=data_dict['item_collection'].name,
        ic_title=data_dict['item_collection'].title)


@app.route('/admin/ic/<ic_id>/reports')
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_report})
@load_models(
    (ItemCollection, {'id': 'ic_id'}, 'item_collection'),
    permission='org_admin')
def admin_report(item_collection):
    return dict(item_collection=item_collection)


def jsonify_org_report(data_dict):
    return jsonify(org_title=data_dict['organization'].title, siteadmin=data_dict['siteadmin'])


@app.route('/admin/o/<org_name>/reports')
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_org_report})
@load_models(
    (Organization, {'name': 'org_name'}, 'organization'),
    permission='org_admin')
def admin_org_report(organization):
    return dict(organization=organization, siteadmin=lastuser.has_permission('siteadmin'))


@app.route('/admin/ic/<ic_id>/tickets.csv')
@lastuser.requires_login
@load_models(
    (ItemCollection, {'id': 'ic_id'}, 'item_collection'),
    permission='org_admin')
def tickets_report(item_collection):
    headers, rows = item_collection.fetch_all_details()
    assignee_url_index = headers.index('assignee_url')

    def row_handler(row):
        # localize datetime
        row_list = [v if not isinstance(v, datetime) else format_datetime(localize_timezone(v), format='long', locale=get_locale()) for v in row]
        # add assignee url
        access_token = row_list[assignee_url_index]
        if access_token:
            row_list[assignee_url_index] = url_for('line_items', access_token=access_token, _external=True)
        return row_list

    return csv_response(headers, rows, row_handler=row_handler)


@app.route('/admin/ic/<ic_id>/attendees.csv')
@lastuser.requires_login
@load_models(
    (ItemCollection, {'id': 'ic_id'}, 'item_collection'),
    permission='org_admin')
def attendees_report(item_collection):
    # Generated a unique list of headers for all 'assignee_details' keys in all items in this item collection. This flattens the 'assignee_details' dict. This will need to be updated if we add additional dicts to our csv export.
    attendee_details_headers = []
    for item in item_collection.items:
        if item.assignee_details:
            for detail in item.assignee_details.keys():
                attendee_detail_prefixed = 'attendee_details_' + detail
                # Eliminate duplicate headers across attendee_details across items. For example, if 't-shirt' and 'hoodie' are two items with a 'size' key, you only want one column in the csv called size.
                if attendee_detail_prefixed not in attendee_details_headers:
                    attendee_details_headers.append(attendee_detail_prefixed)

    headers, rows = item_collection.fetch_assignee_details()
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
                dict_row[headers[idx]] = format_datetime(localize_timezone(item), format='long', locale=get_locale())
            # Item is a string, add it to the dict with the corresponding key
            else:
                dict_row[headers[idx]] = item
        return dict_row

    csv_headers = list(headers)
    # Remove 'attendee_details' from header
    if 'attendee_details' in headers:
        csv_headers.remove('attendee_details')

    return csv_response(csv_headers, rows, row_type='dict', row_handler=row_handler)


@app.route('/api/1/organization/<org>/ic/<ic_id>/orders.csv')
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    (ItemCollection, {'id': 'ic_id', 'organization': 'organization'}, 'item_collection')
    )
def orders_api(organization, item_collection):
    check_api_access(organization.details.get('access_token'))

    # Generated a unique list of headers for all 'assignee_details' keys in all items in this item collection. This flattens the 'assignee_details' dict. This will need to be updated if we add additional dicts to our csv export.
    attendee_details_headers = []
    for item in item_collection.items:
        if item.assignee_details:
            for detail in item.assignee_details.keys():
                attendee_detail_prefixed = 'attendee_details_' + detail
                # Eliminate duplicate headers across attendee_details across items. For example, if 't-shirt' and 'hoodie' are two items with a 'size' key, you only want one column in the csv called size.
                if attendee_detail_prefixed not in attendee_details_headers:
                    attendee_details_headers.append(attendee_detail_prefixed)
    headers, rows = item_collection.fetch_all_details()
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
                dict_row[headers[idx]] = format_datetime(localize_timezone(item), format='long', locale=get_locale() or 'en')  # FIXME: How to handle locale where the accept langauges header isn't specified? Relevant issue in baseframe https://github.com/hasgeek/baseframe/issues/154
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
    (Organization, {'name': 'org_name'}, 'organization'),
    permission='org_admin')
def invoices_report(organization):
    headers, rows = organization.fetch_invoices()

    def row_handler(row):
        dict_row = dict(list(zip(headers, row)))
        if dict_row.get('status') in INVOICE_STATUS.keys():
            dict_row['status'] = INVOICE_STATUS.get(dict_row['status'])
        if isinstance(dict_row.get('invoiced_at'), datetime):
            dict_row['invoiced_at'] = format_datetime(localize_timezone(dict_row['invoiced_at']), format='long', locale=get_locale() or 'en')
        return dict_row

    return csv_response(headers, rows, row_type='dict', row_handler=row_handler)


@app.route('/admin/o/<org_name>/settlements.csv')
@lastuser.requires_permission('siteadmin')
@load_models(
    (Organization, {'name': 'org_name'}, 'organization'))
def settled_transactions(organization):
    year = int(request.args.get('year'))
    month = int(request.args.get('month'))
    try:
        date(year, month, 1)
    except (ValueError, TypeError):
        return api_error(message='Invalid year/month',
                status_code=403,
                errors=['invalid_date'])
    headers, rows = get_settled_transactions({'year': year, 'month': month}, g.user.timezone)
    return csv_response(headers, rows, row_type='dict')
