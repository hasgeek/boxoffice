from flask import jsonify, request

from baseframe import _
from baseframe.forms import render_form
from coaster.views import load_models, render_with

from .. import app, lastuser
from ..forms import CategoryForm
from ..models import Category, ItemCollection, db
from .utils import api_error, api_success


def jsonify_new_category(data_dict):
    item_collection = data_dict['item_collection']
    category_form = CategoryForm(parent=item_collection)
    if request.method == 'GET':
        return jsonify(
            form_template=render_form(
                form=category_form, title="New item", submit="Create", with_chrome=False
            ).get_data(as_text=True)
        )
    if category_form.validate_on_submit():
        category = Category(item_collection=item_collection)
        category_form.populate_obj(category)
        if not category.name:
            category.make_name()
        db.session.add(category)
        db.session.commit()
        return api_success(
            result={'category': dict(category.current_access())},
            doc=_("New category created"),
            status_code=201,
        )
    return api_error(
        message=_("There was a problem with creating the item"),
        errors=category_form.errors,
        status_code=400,
    )


@app.route('/admin/ic/<ic_id>/category/new', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with(
    {'text/html': 'index.html.jinja2', 'application/json': jsonify_new_category}
)
@load_models(
    (ItemCollection, {'id': 'ic_id'}, 'item_collection'), permission='org_admin'
)
def admin_new_category(item_collection):
    return {'item_collection': item_collection}


def jsonify_edit_category(data_dict):
    category = data_dict['category']
    category_form = CategoryForm(obj=category)
    if request.method == 'GET':
        return jsonify(
            form_template=render_form(
                form=category_form,
                title="Edit category",
                submit="Update",
                with_chrome=False,
            ).get_data(as_text=True)
        )
    if category_form.validate_on_submit():
        category_form.populate_obj(category)
        db.session.commit()
        return api_success(
            result={'category': dict(category.current_access())},
            doc=_("Category was updated"),
            status_code=201,
        )
    return api_error(
        message=_("There was a problem with updating the category"),
        errors=category_form.errors,
        status_code=400,
    )


@app.route('/admin/ic/<ic_id>/category/<category_id>/edit', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with(
    {'text/html': 'index.html.jinja2', 'application/json': jsonify_edit_category}
)
@load_models((Category, {'id': 'category_id'}, 'category'), permission='org_admin')
def admin_edit_category(category):
    return {'category': category}
