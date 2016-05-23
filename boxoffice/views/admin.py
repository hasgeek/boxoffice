from flask import g, jsonify
from .. import app, lastuser
from coaster.views import load_models, render_with
from boxoffice.models import Organization


def jsonify_dashboard(data):
    return jsonify(orgs=[{'id': org.id, 'name': org.name, 'title': org.title, 'url': '/o/'+org.name}
        for org in data['user'].orgs])


@app.route('/admin')
@lastuser.requires_login
@render_with({'text/html': 'index.html', 'application/json': jsonify_dashboard}, json=True)
def index():
    return dict(user=g.user)


def jsonify_org(data):
    return jsonify(id=data['org'].id,
        name=data['org'].name,
        title=data['org'].title,
        item_collections=[{'id': ic.id, 'name': ic.name, 'title': ic.title, 'url': '/ic/' + unicode(ic.id)} for ic in data['org'].item_collections])


@app.route('/admin/o/<org>')
@lastuser.requires_login
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    permission='admin'
    )
@render_with({'text/html': 'index.html', 'application/json': jsonify_org}, json=True)
def org(organization):
    return dict(org=organization)
