# -*- coding: utf-8 -*-

import datetime
from flask import g, jsonify, request, abort
from .. import app, lastuser
from baseframe import localize_timezone
from coaster.views import load_models, render_with
from boxoffice.models import Organization, ItemCollection
from boxoffice.models.line_item import calculate_weekly_sales


def jsonify_dashboard(data):
    return jsonify(orgs=[{'id': org.id, 'name': org.name, 'title': org.title, 'url': '/o/'+org.name, 'contact_email': org.contact_email, 'details': org.details}
        for org in data['user'].orgs])


@app.route('/admin')
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


@app.route('/admin/o/<org>')
@lastuser.requires_login
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    permission='org_admin'
    )
@render_with({'text/html': 'index.html', 'application/json': jsonify_org}, json=True)
def org(organization):
    return dict(org=organization, title=organization.title)


@app.route('/admin/o/<org>/revenue')
@load_models(
    (Organization, {'name': 'org'}, 'organization')
    )
def org_revenue(organization):
    if not request.args.get('access_token') or request.args.get('access_token') != organization.details.get("access_token"):
        abort(401)
    item_collection_ids = [item_collection.id for item_collection in organization.item_collections]
    timezone = g.user.timezone if g.user else app.config.get('TIMEZONE')
    year = int(request.args.get('year')) if request.args.get('year') else localize_timezone(datetime.datetime.utcnow(), tz=timezone).year
    return jsonify(weekly_sales=calculate_weekly_sales(item_collection_ids, timezone, year))
