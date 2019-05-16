# -*- coding: utf-8 -*-

from flask import g, jsonify, request
import pytz
from .. import app, lastuser
from coaster.views import load_models, render_with
from coaster.utils import getbool
from baseframe import _
from boxoffice.models import Organization, ItemCollection
from boxoffice.models.line_item import calculate_weekly_sales
from boxoffice.models.payment import calculate_weekly_refunds
from boxoffice.views.utils import check_api_access, api_error, api_success


def jsonify_dashboard(data):
    return jsonify(orgs=[{'id': org.id, 'name': org.name, 'title': org.title, 'url': '/o/' + org.name, 'contact_email': org.contact_email, 'details': org.details}
        for org in data['user'].orgs])


@app.route('/admin/')
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_dashboard})
def index():
    return dict(user=g.user)


def jsonify_org(data):
    item_collections_list = ItemCollection.query.filter(ItemCollection.organization == data['org']).order_by(ItemCollection.created_at.desc()).all()
    return jsonify(id=data['org'].id,
        org_title=data['org'].title,
        item_collections=[dict(ic.current_access()) for ic in item_collections_list])


@app.route('/admin/o/<org>')
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_org})
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    permission='org_admin'
    )
def org(organization):
    return dict(org=organization, title=organization.title)


@app.route('/api/1/organization/<org>/weekly_revenue', methods=['GET', 'OPTIONS'])
@load_models(
    (Organization, {'name': 'org'}, 'organization')
    )
def org_revenue(organization):
    check_api_access(organization.details.get('access_token'))

    if not request.args.get('year'):
        return api_error(message=_(u"Missing year"), status_code=400)

    if not request.args.get('timezone'):
        return api_error(message=_(u"Missing timezone"), status_code=400)

    if request.args.get('timezone') not in pytz.common_timezones:
        return api_error(message=_(u"Unknown timezone. Timezone is case-sensitive"), status_code=400)

    item_collection_ids = [item_collection.id for item_collection in organization.item_collections]
    year = int(request.args.get('year'))
    user_timezone = request.args.get('timezone')

    if getbool(request.args.get('refund')):
        result = calculate_weekly_refunds(item_collection_ids, user_timezone, year).items()
        doc = _(u"Refunds per week for {year}".format(year=year))
    else:
        # sales includes confirmed and cancelled line items
        result = calculate_weekly_sales(item_collection_ids, user_timezone, year).items()
        doc = _(u"Revenue per week for {year}".format(year=year))
    return api_success(result=result, doc=doc, status_code=200)
