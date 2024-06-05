from flask import render_template, request
from flask.typing import ResponseReturnValue

from baseframe import _, localize_timezone
from baseframe.forms import render_form
from coaster.auth import current_auth
from coaster.utils import utcnow
from coaster.views import load_models

from .. import app, lastuser
from ..forms import MenuForm
from ..models import Menu, Organization, db
from ..models.line_item import counts_per_date_per_item, sales_by_date, sales_delta
from .admin_ticket import format_ticket_details
from .utils import api_error, api_success, request_wants_json


@app.route('/admin/menu/<menu_id>')
@lastuser.requires_login
@load_models((Menu, {'id': 'menu_id'}, 'menu'), permission='org_admin')
def admin_menu(menu: Menu) -> ResponseReturnValue:
    ticket_ids = [str(ticket.id) for ticket in menu.tickets]
    date_ticket_counts = {}
    date_sales = {}
    for sales_date, sales_count in counts_per_date_per_item(
        menu, current_auth.user.timezone
    ).items():
        date_sales[sales_date.isoformat()] = sales_by_date(
            sales_date, ticket_ids, current_auth.user.timezone
        )
        date_ticket_counts[sales_date.isoformat()] = sales_count
    today_sales = date_sales.get(
        localize_timezone(utcnow(), current_auth.user.timezone).date().isoformat(), 0
    )
    if not request_wants_json():
        return render_template('index.html.jinja2', title=menu.title)
    return {
        'account_name': menu.organization.name,
        'account_title': menu.organization.title,
        'menu_name': menu.name,
        'menu_title': menu.title,
        'categories': [
            {
                'title': category.title,
                'id': category.id,
                'tickets': [
                    format_ticket_details(ticket) for ticket in category.tickets
                ],
            }
            for category in menu.categories
        ],
        'date_ticket_counts': date_ticket_counts,
        'date_sales': date_sales,
        'today_sales': today_sales,
        'net_sales': menu.net_sales(),
        'sales_delta': sales_delta(current_auth.user.timezone, ticket_ids),
    }


@app.route('/admin/o/<org>/menu/new', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models((Organization, {'name': 'org'}, 'organization'), permission='org_admin')
def admin_new_ic(organization: Organization) -> ResponseReturnValue:
    if not request_wants_json():
        return render_template('index.html.jinja2')

    ic_form = MenuForm()
    if request.method == 'GET':
        return {
            'form_template': render_form(
                form=ic_form,
                title=_("New menu"),
                submit=_("Create"),
                ajax=False,
                with_chrome=False,
            ).get_data(as_text=True)
        }
    if ic_form.validate_on_submit():
        menu = Menu(organization=organization)
        ic_form.populate_obj(menu)
        if not menu.name:
            menu.make_name()
        db.session.add(menu)
        db.session.commit()
        return api_success(
            result={'menu': dict(menu.current_access())},
            doc=_("New menu created"),
            status_code=201,
        )
    return api_error(
        message=_("There was a problem with creating the menu"),
        errors=ic_form.errors,
        status_code=400,
    )


@app.route('/admin/menu/<menu_id>/edit', methods=['POST', 'GET'])
@lastuser.requires_login
@load_models((Menu, {'id': 'menu_id'}, 'menu'), permission='org_admin')
def admin_edit_ic(menu: Menu) -> ResponseReturnValue:
    if not request_wants_json():
        return render_template('index.html.jinja2')

    ic_form = MenuForm(obj=menu)
    if request.method == 'GET':
        return {
            'form_template': render_form(
                form=ic_form,
                title=_("Edit menu"),
                submit=_("Save"),
                ajax=False,
                with_chrome=False,
            ).get_data(as_text=True)
        }
    if ic_form.validate_on_submit():
        ic_form.populate_obj(menu)
        db.session.commit()
        return api_success(
            result={'menu': dict(menu.current_access())},
            doc=_("Edited menu {title}.").format(title=menu.title),
            status_code=200,
        )
    return api_error(
        message=_("There was a problem with editing the menu"),
        errors=ic_form.errors,
        status_code=400,
    )
