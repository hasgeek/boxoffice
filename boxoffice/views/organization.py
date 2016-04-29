from flask import url_for, request, jsonify, make_response
from coaster.views import render_with, load_models
from .. import app, lastuser
from ..models import Organization, ItemCollection, Price
from utils import xhr_only


def jsonify_organizations(data):
    organizations = []
    if data['organizations']:
        for org in data['organizations']:
            org_detail = {
                'id': org.id,
                'name': org.name,
                'title': org.title,
                'details': org.details,
                'contact_email': org.contact_email,
                'url': url_for('view_organization', organization=org.name)
            }
            organizations.append(org_detail)
    return jsonify(organizations=organizations)


def jsonify_item_collections(data):
    org = data['org']
    item_collections = []
    if data['item_collections']:
        for item_collection in data['item_collections']:
            item_collection_detail = {
                'id': item_collection.id,
                'name': item_collection.name,
                'title': item_collection.title,
                'description_text': item_collection.description_text,
                'description_html': item_collection.description_html,
                'url': url_for('view_item_collection', organization=org.name, item_collection=item_collection.name)
            }
            item_collections.append(item_collection_detail)
    return jsonify(item_collections=item_collections)


@app.route('/', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with({'text/html': 'organization.html', 'application/json': jsonify_organizations}, json=True)
def index():
    organizations = Organization.query.all()
    return dict(organizations=organizations)


@app.route('/organization/new', methods=['GET', 'POST'])
@lastuser.requires_login
@xhr_only
def add_organization(organization):
    # Add organization
    return make_response(jsonify(message="Organization added"), 201)


@app.route('/<organization>', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with({'text/html': 'list_item_collection.html', 'application/json': jsonify_item_collections}, json=True)
@load_models(
    (Organization, {'name': 'organization'}, 'organization')
    )
def view_organization(organization):
    item_collections = ItemCollection.query.filter_by(organization=organization).all()
    return dict(org=organization, item_collections=item_collections)


@app.route('/<organization>/edit', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (Organization, {'id': 'organization'}, 'organization')
    )
@xhr_only
def update_organization(organization):
    # Update organization details
    return make_response(jsonify(message="Organization updated"), 201)


@app.route('/<organization>/delete', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (Organization, {'id': 'organization'}, 'organization')
    )
@xhr_only
def delete_organization(organization):
    # Delete organization
    return make_response(jsonify(message="Organization deleted"), 201)
