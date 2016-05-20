from flask import g, jsonify, make_response, render_template
from .. import app, lastuser
from coaster.views import load_models, render_with
from boxoffice.models import Organization


@app.route('/admin')
@lastuser.requires_login
def index():
    # return make_response(jsonify(msg="hello"), 201)
    return render_template('index.html')


def jsonify_org(data):
    return jsonify(id=data['org'].id,
        name=data['org'].name,
        title=data['org'].title,
        item_collections=[{'id': ic.id, 'name': ic.name} for ic in data['org'].item_collections])


@app.route('/admin/o/<org>')
@lastuser.requires_login
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    )
@render_with({'text/html': 'index.html', 'application/json': jsonify_org}, json=True)
def org(organization):
    return dict(org=organization)


@app.route('/admin/dashboard')
@lastuser.requires_login
def dashboard(**args):
    return make_response(jsonify(orgs=[{'id': org.id, 'name': org.name, 'title': org.title, 'url': '/o/'+org.name} for org in g.user.orgs]), 201)


# @app.route('/<org>')
# @lastuser.requires_login
# @load_models(
#     (Organization, {'name': 'org'}, 'org'), permission='org_view')
# def organization(org):
#     return make_response(jsonify(organization=org.title), 201)
