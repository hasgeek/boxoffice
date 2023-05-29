from decimal import Decimal

from flask import g, jsonify, request

from baseframe import _, localize_timezone
from baseframe.forms import render_form
from coaster.utils import utcnow
from coaster.views import load_models, render_with

from .. import app, lastuser
from ..forms import ItemCollectionForm
from ..models import ItemCollection, Organization, db
from ..models.line_item import counts_per_date_per_item, sales_by_date, sales_delta
from .admin_item import format_item_details
from .utils import api_error, api_success


def jsonify_item_collection(item_collection_dict):
    return jsonify(
        account_name=item_collection_dict['item_collection'].organization.name,
        account_title=item_collection_dict['item_collection'].organization.title,
        menu_name=item_collection_dict['item_collection'].name,
        menu_title=item_collection_dict['item_collection'].title,
        categories=[
            {
                'title': category.title,
                'id': category.id,
                'items': [format_item_details(item) for item in category.items],
            }
            for category in item_collection_dict['item_collection'].categories
        ],
        date_item_counts=item_collection_dict['date_item_counts'],
        date_sales=item_collection_dict['date_sales'],
        today_sales=item_collection_dict['today_sales'],
        net_sales=item_collection_dict['item_collection'].net_sales(),
        sales_delta=item_collection_dict['sales_delta'],
    )


@app.route('/admin/menu/<menu_id>')
@lastuser.requires_login
@render_with(
    {'text/html': 'index.html.jinja2', 'application/json': jsonify_item_collection}
)
@load_models(
    (ItemCollection, {'id': 'menu_id'}, 'item_collection'), permission='org_admin'
)
def admin_item_collection(item_collection):
    item_ids = [str(item.id) for item in item_collection.items]
    date_item_counts = {}
    date_sales = {}
    for sales_date, sales_count in counts_per_date_per_item(
        item_collection, g.user.timezone
    ).items():
        date_sales[sales_date.isoformat()] = sales_by_date(
            sales_date, item_ids, g.user.timezone
        )
        date_item_counts[sales_date.isoformat()] = sales_count
    today_sales = date_sales.get(
        localize_timezone(utcnow(), g.user.timezone).date().isoformat(), Decimal(0)
    )
    return {
        'title': item_collection.title,
        'item_collection': item_collection,
        'date_item_counts': date_item_counts,
        'date_sales': date_sales,
        'today_sales': today_sales,
        'sales_delta': sales_delta(g.user.timezone, item_ids),
    }


def jsonify_new_item_collection(item_collection_dict):
    ic_form = ItemCollectionForm()
    if request.method == 'GET':
        return jsonify(
            form_template=render_form(
                form=ic_form,
                title="New item collection",
                submit="Create",
                ajax=False,
                with_chrome=False,
            ).get_data(as_text=True)
        )
    if ic_form.validate_on_submit():
        menu = ItemCollection(organization=item_collection_dict['organization'])
        ic_form.populate_obj(menu)
        if not menu.name:
            menu.make_name()
        db.session.add(menu)
        db.session.commit()
        return api_success(
            result={'item_collection': dict(menu.current_access())},
            doc=_("New item collection created"),
            status_code=201,
        )
    return api_error(
        message=_("There was a problem with creating the item collection"),
        errors=ic_form.errors,
        status_code=400,
    )


@app.route('/admin/o/<org>/menu/new', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with(
    {'text/html': 'index.html.jinja2', 'application/json': jsonify_new_item_collection}
)
@load_models((Organization, {'name': 'org'}, 'organization'), permission='org_admin')
def admin_new_ic(organization):
    return {'organization': organization}


def jsonify_edit_item_collection(item_collection_dict):
    item_collection = item_collection_dict['item_collection']
    ic_form = ItemCollectionForm(obj=item_collection)
    if request.method == 'GET':
        return jsonify(
            form_template=render_form(
                form=ic_form,
                title="Edit item collection",
                submit="Save",
                ajax=False,
                with_chrome=False,
            ).get_data(as_text=True)
        )
    if ic_form.validate_on_submit():
        ic_form.populate_obj(item_collection)
        db.session.commit()
        return api_success(
            result={'item_collection': dict(item_collection.current_access())},
            doc=_("Edited item collection {title}.").format(
                title=item_collection.title
            ),
            status_code=200,
        )
    return api_error(
        message=_("There was a problem with editing the item collection"),
        errors=ic_form.errors,
        status_code=400,
    )


@app.route('/admin/menu/<menu_id>/edit', methods=['POST', 'GET'])
@lastuser.requires_login
@render_with(
    {'text/html': 'index.html.jinja2', 'application/json': jsonify_edit_item_collection}
)
@load_models(
    (ItemCollection, {'id': 'menu_id'}, 'item_collection'), permission='org_admin'
)
def admin_edit_ic(item_collection):
    return {'item_collection': item_collection}
