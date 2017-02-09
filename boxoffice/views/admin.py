# -*- coding: utf-8 -*-

from flask import g, jsonify, request
from .. import app, lastuser
from coaster.views import load_models, render_with, requestargs
from boxoffice.models import Organization, ItemCollection, Item
from utils import xhr_only


def jsonify_dashboard(data):
    return jsonify(orgs=[{'id': org.id, 'name': org.name, 'title': org.title, 'url': '/o/' + org.name, 'contact_email': org.contact_email, 'details': org.details}
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


@app.route('/admin/o/<org>/items')
@lastuser.requires_login
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    permission='org_admin'
    )
@xhr_only
@requestargs('search')
def admin_items(organization, search=None):
    if search:
        filtered_items = Item.query.filter(Item.title.ilike('%{query}%'.format(query=search))).all()
        return jsonify(items=[{'id': str(item.id), 'title': item.title} for item in filtered_items])
