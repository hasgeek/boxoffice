# -*- coding: utf-8 -*-

from flask import jsonify
from .. import app, lastuser
from coaster.views import load_models, render_with
from baseframe import localize_timezone, get_locale
from boxoffice.models import ItemCollection, LineItem
from boxoffice.views.utils import csv_response
from babel.dates import format_datetime


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
    headers = ['ticket id', 'order id', 'receipt no', 'ticket type', 'base amount', 'discounted amount', 'final amount', 'discount policy', 'discount code', 'buyer fullname', 'buyer email', 'buyer phone', 'attendee fullname', 'attendee email', 'attendee phone', 'attendee details', 'utm_campaign', 'utm_source', 'utm_medium', 'utm_term', 'utm_content', 'utm_id', 'gclid', 'referrer', 'date']
    rows = item_collection.fetch_all_details

    def row_handler(row):
        row_list = list(row)
        # localize datetime
        row_list[-1] = format_datetime(localize_timezone(row_list[-1]), format='long', locale=get_locale())
        return row_list

    return csv_response(headers, rows, row_handler=row_handler)


@app.route('/admin/ic/<ic_id>/attendees.csv')
@lastuser.requires_login
@load_models(
    (ItemCollection, {'id': 'ic_id'}, 'item_collection'),
    permission='org_admin')
def attendees_report(item_collection):
    headers = ['receipt no', 'ticket no', 'ticket id', 'ticket type', 'attendee fullname', 'attendee email', 'attendee phone']
    for item in item_collection.items:
        for detail in item.assignee_details.keys():
            if detail not in headers:
                headers.append(detail)
    rows = item_collection.fetch_assignee_details

    def row_handler(row):
        # Convert row to a dict
        # row[-1] contains attendee details which is already a dict
        dict_row = dict(zip(headers, row[:-1]))
        dict_row.update(row[-1])
        return dict_row

    return csv_response(headers, rows, row_type='dict', row_handler=row_handler)
