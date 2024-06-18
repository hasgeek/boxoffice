from datetime import date

import pytz
from flask import Response, render_template, request
from flask.typing import ResponseReturnValue

from baseframe import _
from coaster.auth import current_auth
from coaster.utils import getbool
from coaster.views import load_models

from .. import app, lastuser
from ..models import Menu, Organization
from ..models.line_item import calculate_weekly_sales
from ..models.payment import calculate_weekly_refunds
from .utils import api_error, api_success, check_api_access, request_wants_json


@app.route('/admin/')
@lastuser.requires_login
def index() -> ResponseReturnValue:
    if not request_wants_json():
        return render_template('index.html.jinja2')
    return {
        'orgs': [
            {
                'id': org.id,
                'name': org.name,
                'title': org.title,
                'url': '/o/' + org.name,
                'contact_email': org.contact_email,
                'details': org.details,
            }
            for org in current_auth.user.orgs
        ]
    }


@app.route('/admin/o/<org>')
@lastuser.requires_login
@load_models((Organization, {'name': 'org'}, 'organization'), permission='org_admin')
def org(organization: Organization) -> ResponseReturnValue:
    if not request_wants_json():
        return render_template('index.html.jinja2', title=organization.title)
    menu_list = (
        Menu.query.filter(Menu.organization_id == organization.id)
        .order_by(Menu.created_at.desc())
        .all()
    )
    return {
        'id': organization.id,
        'account_title': organization.title,
        'menus': [dict(menu.current_access()) for menu in menu_list],
    }


@app.route('/api/1/organization/<org>/weekly_revenue', methods=['GET', 'OPTIONS'])
@load_models((Organization, {'name': 'org'}, 'organization'))
def org_revenue(organization: Organization) -> Response:
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
