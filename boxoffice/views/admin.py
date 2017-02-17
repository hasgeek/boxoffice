# -*- coding: utf-8 -*-

from flask import g, jsonify, request
import pytz
from .. import app, lastuser
from coaster.views import load_models, render_with, requestargs
from boxoffice.models import Organization, ItemCollection, Item
from boxoffice.models.line_item import calculate_weekly_sales
from boxoffice.views.utils import check_api_access, api_error, api_success
from utils import xhr_only


def jsonify_dashboard(data):
    return jsonify(orgs=[{'id': org.id, 'name': org.name, 'title': org.title, 'url': '/o/' + org.name, 'contact_email': org.contact_email, 'details': org.details}
        for org in data['user'].orgs])


@app.route('/api/1/admin/')
@lastuser.requires_login
@render_with({'text/html': 'index.html', 'application/json': jsonify_dashboard}, json=True)
def index():
    return dict(user=g.user)


def jsonify_org(data):
    item_collections_list = ItemCollection.query.filter(ItemCollection.organization == data['org']).order_by('created_at desc').all()
    return jsonify(id=data['org'].id,
        name=data['org'].name,
        title=data['org'].title,
        item_collections=[{'id': ic.id, 'name': ic.name, 'title': ic.title, 'url': '/ic/' + unicode(ic.id), 'description_text': ic.description_text, 'description_html': ic.description_html} for ic in item_collections_list])


@app.route('/api/1/admin/o/<org>')
@lastuser.requires_login
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    permission='org_admin'
    )
@render_with({'text/html': 'index.html', 'application/json': jsonify_org}, json=True)
def org(organization):
    return dict(org=organization, title=organization.title)


@app.route('/api/1/admin/o/<org>/items')
@lastuser.requires_login
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    permission='org_admin'
    )
@xhr_only
@requestargs('search')
def admin_items(organization, search=None):
    if search:
        filtered_items = Item.query.join(ItemCollection).filter(Item.title.ilike('%{query}%'.format(query=search))).all()
        return jsonify(items=[{'id': str(item.id), 'title': item.title} for item in filtered_items])


@app.route('/api/1/organization/<org>/revenue', methods=['GET', 'OPTIONS'])
@load_models(
    (Organization, {'name': 'org'}, 'organization')
    )
def org_revenue(organization):
    check_api_access(organization.details.get('access_token'))
    if not request.args.get('year'):
        return api_error(message='Missing year.', status_code=400)

    if not request.args.get('timezone'):
        return api_error(message='Missing timezone.', status_code=400)

    user_timezone = request.args.get('timezone')
    if user_timezone not in pytz.common_timezones:
        return api_error(message='Unknown timezone. timezone is case-sensitive.', status_code=400)

    item_collection_ids = [item_collection.id for item_collection in organization.item_collections]
    year = int(request.args.get('year'))
    weekly_sales = calculate_weekly_sales(item_collection_ids, user_timezone, year).items()
    return api_success(result=weekly_sales, doc="Revenue per week for {year}".format(year=year), status_code=200)
