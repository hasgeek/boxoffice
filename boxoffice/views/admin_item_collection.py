from flask import g, jsonify, request

from baseframe import _, localize_timezone
from baseframe.forms import render_form
from coaster.utils import utcnow
from coaster.views import ReturnRenderWith, load_models, render_with

from .. import app, lastuser
from ..forms import ItemCollectionForm
from ..models import ItemCollection, Organization, db
from ..models.line_item import counts_per_date_per_item, sales_by_date, sales_delta
from .admin_item import format_ticket_details
from .utils import api_error, api_success


def jsonify_menu(menu_dict):
    return jsonify(
        account_name=menu_dict['menu'].organization.name,
        account_title=menu_dict['menu'].organization.title,
        menu_name=menu_dict['menu'].name,
        menu_title=menu_dict['menu'].title,
        categories=[
            {
                'title': category.title,
                'id': category.id,
                'tickets': [
                    format_ticket_details(ticket) for ticket in category.tickets
                ],
            }
            for category in menu_dict['menu'].categories
        ],
        date_ticket_counts=menu_dict['date_ticket_counts'],
        date_sales=menu_dict['date_sales'],
        today_sales=menu_dict['today_sales'],
        net_sales=menu_dict['menu'].net_sales(),
        sales_delta=menu_dict['sales_delta'],
    )


@app.route('/admin/menu/<menu_id>')
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_menu})
@load_models((ItemCollection, {'id': 'menu_id'}, 'menu'), permission='org_admin')
def admin_menu(menu: ItemCollection) -> ReturnRenderWith:
    ticket_ids = [str(ticket.id) for ticket in menu.tickets]
    date_ticket_counts = {}
    date_sales = {}
    for sales_date, sales_count in counts_per_date_per_item(
        menu, g.user.timezone
    ).items():
        date_sales[sales_date.isoformat()] = sales_by_date(
            sales_date, ticket_ids, g.user.timezone
        )
        date_ticket_counts[sales_date.isoformat()] = sales_count
    today_sales = date_sales.get(
        localize_timezone(utcnow(), g.user.timezone).date().isoformat(), 0
    )
    return {
        'title': menu.title,
        'menu': menu,
        'date_ticket_counts': date_ticket_counts,
        'date_sales': date_sales,
        'today_sales': today_sales,
        'sales_delta': sales_delta(g.user.timezone, ticket_ids),
    }


def jsonify_new_menu(menu_dict):
    ic_form = ItemCollectionForm()
    if request.method == 'GET':
        return jsonify(
            form_template=render_form(
                form=ic_form,
                title="New menu",
                submit="Create",
                ajax=False,
                with_chrome=False,
            ).get_data(as_text=True)
        )
    if ic_form.validate_on_submit():
        menu = ItemCollection(organization=menu_dict['organization'])
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


@app.route('/admin/o/<org>/menu/new', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_new_menu})
@load_models((Organization, {'name': 'org'}, 'organization'), permission='org_admin')
def admin_new_ic(organization: Organization) -> ReturnRenderWith:
    return {'organization': organization}


def jsonify_edit_menu(menu_dict):
    menu = menu_dict['menu']
    ic_form = ItemCollectionForm(obj=menu)
    if request.method == 'GET':
        return jsonify(
            form_template=render_form(
                form=ic_form,
                title="Edit menu",
                submit="Save",
                ajax=False,
                with_chrome=False,
            ).get_data(as_text=True)
        )
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


@app.route('/admin/menu/<menu_id>/edit', methods=['POST', 'GET'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_edit_menu})
@load_models((ItemCollection, {'id': 'menu_id'}, 'menu'), permission='org_admin')
def admin_edit_ic(menu: ItemCollection) -> ReturnRenderWith:
    return {'menu': menu}
