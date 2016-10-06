# -*- coding: utf-8 -*-

from flask import jsonify
from .. import app, lastuser
from coaster.views import load_models, render_with
from boxoffice.models import ItemCollection, LineItem
from boxoffice.views.utils import csv_response


def jsonify_report(data_dict):
    return jsonify(org_name=data_dict['item_collection'].organization.name, item_collection_title=data_dict['item_collection'].title)


@app.route('/admin/ic/<id>/reports')
@lastuser.requires_login
@load_models(
    (ItemCollection, {'id': 'id'}, 'item_collection'),
    permission='org_admin')
@render_with({'text/html': 'index.html', 'application/json': jsonify_report})
def admin_report(item_collection):
    return dict(title=item_collection.organization.title, item_collection=item_collection)


@app.route('/admin/ic/<id>/reports/tickets.csv')
@lastuser.requires_login
@load_models(
    (ItemCollection, {'id': 'id'}, 'item_collection'),
    permission='org_admin')
def admin_line_items_report(item_collection):
    headers = ['ticket id', 'item title', 'base amount', 'discounted amount', 'final amount', 'discount policy', 'buyer fullname', 'buyer email', 'buyer phone', 'attendee fullname', 'attendee email', 'attendee phone', 'attendee details']
    rows = LineItem.fetch_all_details(item_collection)
    return csv_response(headers, rows)
