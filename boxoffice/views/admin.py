# -*- coding: utf-8 -*-

from flask import g, jsonify
from .. import app, lastuser
from coaster.views import load_models, render_with
from boxoffice.models import Organization, ItemCollection


def jsonify_dashboard(data):
    return jsonify(orgs=[{'id': org.id, 'name': org.name, 'title': org.title, 'url': '/o/'+org.name, 'contact_email': org.contact_email, 'details': org.details}
        for org in data['user'].orgs])


@app.route('/admin')
@lastuser.requires_login
@render_with({'text/html': 'index.html', 'application/json': jsonify_dashboard}, json=True)
def index():
    return dict(user=g.user)


def jsonify_org(data):
    item_collections = []
    for item_collection in ItemCollection.query.filter(ItemCollection.organization == data['org']).order_by('created_at desc'):
        item_collections.append({'id': item_collection.id,
            'name': item_collection.name,
            'title': item_collection.title,
            'url': '/ic/' + unicode(item_collection.id),
            'description_text': item_collection.description_text,
            'description_html': item_collection.description_html})
    return jsonify(id=data['org'].id,
        name=data['org'].name,
        title=data['org'].title,
        item_collections=item_collections)


@app.route('/admin/o/<org>')
@lastuser.requires_login
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    permission='org_admin'
    )
@render_with({'text/html': 'index.html', 'application/json': jsonify_org}, json=True)
def org(organization):
    return dict(org=organization, title=organization.title)
