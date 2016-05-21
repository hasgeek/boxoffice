from flask import g, jsonify, make_response, render_template
from .. import app, lastuser
from coaster.views import load_models, render_with
from boxoffice.models import Organization, ItemCollection, LineItem, LINE_ITEM_STATUS


@app.route('/admin')
@lastuser.requires_login
def index():
    # return make_response(jsonify(msg="hello"), 201)
    return render_template('index.html')


def jsonify_org(data):
    return jsonify(id=data['org'].id,
        name=data['org'].name,
        title=data['org'].title,
        item_collections=[{'id': ic.id, 'name': ic.name, 'title': ic.title, 'url': '/ic/' + unicode(ic.id)} for ic in data['org'].item_collections])


@app.route('/admin/o/<org>')
@lastuser.requires_login
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    )
@render_with({'text/html': 'index.html', 'application/json': jsonify_org}, json=True)
def org(organization):
    return dict(org=organization)


def jsonify_item(item):
    sold = LineItem.query.filter(LineItem.item == item, LineItem.final_amount > 0, LineItem.status == LINE_ITEM_STATUS.CONFIRMED).count()
    free = LineItem.query.filter(LineItem.item == item, LineItem.final_amount == 0, LineItem.status == LINE_ITEM_STATUS.CONFIRMED).count()
    cancelled = LineItem.query.filter(LineItem.item == item, LineItem.status == LINE_ITEM_STATUS.CANCELLED).count()
    available = item.quantity_total - (sold + free - cancelled)
    return {
        'id': item.id,
        'title': item.title,
        'available': available,
        'sold': sold,
        'free': free,
        'cancelled': cancelled
    }


def jsonify_item_collection(item_collection_dict):
    return jsonify(items=[jsonify_item(item)
        for item in item_collection_dict['item_collection'].items])


@app.route('/admin/ic/<ic_id>')
@lastuser.requires_login
@load_models(
    (ItemCollection, {'id': 'ic_id'}, 'item_collection'),
    )
@render_with({'text/html': 'index.html', 'application/json': jsonify_item_collection}, json=True)
def admin_item_collection(item_collection):
    return dict(item_collection=item_collection)


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
