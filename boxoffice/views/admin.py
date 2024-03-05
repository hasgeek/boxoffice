from datetime import date

from flask import g, jsonify, request
import pytz

from baseframe import _
from coaster.utils import getbool
from coaster.views import ReturnRenderWith, load_models, render_with

from .. import app, lastuser
from ..models import ItemCollection, Organization
from ..models.line_item import calculate_weekly_sales
from ..models.payment import calculate_weekly_refunds
from .utils import api_error, api_success, check_api_access


def jsonify_dashboard(data):
    return jsonify(
        orgs=[
            {
                'id': org.id,
                'name': org.name,
                'title': org.title,
                'url': '/o/' + org.name,
                'contact_email': org.contact_email,
                'details': org.details,
            }
            for org in data['user'].orgs
        ]
    )


@app.route('/admin/')
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_dashboard})
def index() -> ReturnRenderWith:
    return {'user': g.user}


def jsonify_org(data):
    menu_list = (
        ItemCollection.query.filter(ItemCollection.organization == data['org'])
        .order_by(ItemCollection.created_at.desc())
        .all()
    )
    return jsonify(
        id=data['org'].id,
        account_title=data['org'].title,
        menus=[dict(menu.current_access()) for menu in menu_list],
    )


@app.route('/admin/o/<org>')
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_org})
@load_models((Organization, {'name': 'org'}, 'organization'), permission='org_admin')
def org(organization: Organization) -> ReturnRenderWith:
    return {'org': organization, 'title': organization.title}


@app.route('/api/1/organization/<org>/weekly_revenue', methods=['GET', 'OPTIONS'])
@load_models((Organization, {'name': 'org'}, 'organization'))
def org_revenue(organization: Organization):
    check_api_access(organization.details.get('access_token'))

    if not request.args.get('year'):
        return api_error(message=_("Missing year"), status_code=400)

    if not request.args.get('timezone'):
        return api_error(message=_("Missing timezone"), status_code=400)

    if request.args.get('timezone') not in pytz.common_timezones:
        return api_error(
            message=_("Unknown timezone. Timezone is case-sensitive"), status_code=400
        )

    menu_ids = [menu.id for menu in organization.menus]
    year = int(request.args.get('year') or date.today().year)
    user_timezone: str = request.args.get('timezone') or app.config['TIMEZONE']

    if getbool(request.args.get('refund')):
        result = list(calculate_weekly_refunds(menu_ids, user_timezone, year).items())
        doc = _("Refunds per week for {year}").format(year=year)
    else:
        # sales includes confirmed and cancelled line items
        result = list(calculate_weekly_sales(menu_ids, user_timezone, year).items())
        doc = _("Revenue per week for {year}").format(year=year)
    return api_success(result=result, doc=doc, status_code=200)
