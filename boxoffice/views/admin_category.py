"""Menu category management views."""

from flask import render_template, request
from flask.typing import ResponseReturnValue

from baseframe import _
from baseframe.forms import render_form
from coaster.views import load_models

from .. import app, lastuser
from ..forms import CategoryForm
from ..models import Category, Menu, db
from .utils import api_error, api_success, request_wants_json


@app.route('/admin/menu/<menu_id>/category/new', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models((Menu, {'uuid_hex': 'menu_id'}, 'menu'), permission='org_admin')
def admin_new_category(menu: Menu) -> ResponseReturnValue:
    if not request_wants_json():
        return render_template('index.html.jinja2')
    category_form = CategoryForm(parent=menu)
    if request.method == 'GET':
        return {
            'form_template': render_form(
                form=category_form,
                title=_("New Ticket"),
                submit=_("Create"),
                with_chrome=False,
            ).get_data(as_text=True)
        }
    if category_form.validate_on_submit():
        category = Category(menu=menu)
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
        message=_("There was a problem with creating the ticket"),
        errors=category_form.errors,
        status_code=400,
    )


@app.route('/admin/menu/<menu_id>/category/<category_id>/edit', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models((Category, {'id': 'category_id'}, 'category'), permission='org_admin')
def admin_edit_category(category: Category) -> ResponseReturnValue:
    if not request_wants_json():
        return render_template('index.html.jinja2')
    category_form = CategoryForm(obj=category)
    if request.method == 'GET':
        return {
            'form_template': render_form(
                form=category_form,
                title=_("Edit category"),
                submit=_("Update"),
                with_chrome=False,
            ).get_data(as_text=True)
        }
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
