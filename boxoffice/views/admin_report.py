# -*- coding: utf-8 -*-

from flask import jsonify
from .. import app, lastuser
from coaster.views import load_models, render_with
from baseframe import localize_timezone, get_locale
from boxoffice.models import Organization, ItemCollection, LineItem
from boxoffice.views.utils import check_api_access, csv_response
from babel.dates import format_datetime
from datetime import datetime


def jsonify_report(data_dict):
    return jsonify(org_name=data_dict['item_collection'].organization.name,
        name=data_dict['item_collection'].name,
        title=data_dict['item_collection'].title)


@app.route('/admin/ic/<ic_id>/reports')
@lastuser.requires_login
@render_with({'text/html': 'index.html', 'application/json': jsonify_report})
@load_models(
    (ItemCollection, {'id': 'ic_id'}, 'item_collection'),
    permission='org_admin')
def admin_report(item_collection):
    return dict(item_collection=item_collection)


@app.route('/admin/ic/<ic_id>/tickets.csv')
@lastuser.requires_login
@load_models(
    (ItemCollection, {'id': 'ic_id'}, 'item_collection'),
    permission='org_admin')
def tickets_report(item_collection):
    headers, rows = item_collection.fetch_all_details()
    def row_handler(row):
        # localize datetime
        row_list = [v if not isinstance(v, datetime) else format_datetime(localize_timezone(v), format='long', locale=get_locale()) for v in list(row)]
        return row_list

    return csv_response(headers, rows, row_handler=row_handler)


@app.route('/admin/ic/<ic_id>/attendees.csv')
@lastuser.requires_login
@load_models(
    (ItemCollection, {'id': 'ic_id'}, 'item_collection'),
    permission='org_admin')
def attendees_report(item_collection):

    attendee_details_headers = []
    for item in item_collection.items:
        if item.assignee_details:
            for detail in item.assignee_details.keys():
                attendee_detail_prefexed = 'attendee_details_' + detail
                if attendee_detail_prefexed not in attendee_details_headers:
                    attendee_details_headers.append(attendee_detail_prefexed)

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
            # 'assignee_details' is a dict already, so copy and include prefixs
            if idx == attendee_details_index and isinstance(item, dict):
                for key in item.keys():
                    dict_row['attendee_details_'+key] = item[key]
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
    attendee_details_headers = []
    for item in item_collection.items:
        if item.assignee_details:
            for detail in item.assignee_details.keys():
                attendee_detail_prefexed = 'attendee_details_' + detail
                if attendee_detail_prefexed not in attendee_details_headers:
                    attendee_details_headers.append(attendee_detail_prefexed)
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
                    dict_row['attendee_details_'+key] = item[key]
            # Item is a datetime object, so format and add to dict
            elif isinstance(item, datetime):
                dict_row[headers[idx]] = format_datetime(localize_timezone(item), format='long', locale=get_locale())
            # Value is a string, add it to the dict with the corresponding key
            else:
                dict_row[headers[idx]] = item
        return dict_row

    csv_headers = list(headers)
    # Remove 'attendee_details' from header
    if 'attendee_details' in headers:
        csv_headers.remove('attendee_details')

    return csv_response(csv_headers, rows, row_type='dict', row_handler=row_handler)
