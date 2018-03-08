# -*- coding: utf-8 -*-

from flask import jsonify, request
from .. import app, lastuser
from coaster.views import load_models, render_with
from baseframe import _
from baseframe.forms import render_form
from boxoffice.models import db, ItemCollection, Category
from boxoffice.views.utils import api_error, api_success
from boxoffice.forms import CategoryForm


def jsonify_new_category(data_dict):
    item_collection = data_dict['item_collection']
    category_form = CategoryForm(parent=item_collection)
    if request.method == 'GET':
        return jsonify(form_template=render_form(form=category_form, title=u"New item", submit=u"Create", with_chrome=False))
    if category_form.validate_on_submit():
        category = Category(item_collection=item_collection)
        category_form.populate_obj(category)
        if not category.name:
            category.make_name()
        db.session.add(category)
        db.session.commit()
        return api_success(result={'category': dict(category.current_access())}, doc=_(u"New category created"), status_code=201)
    return api_error(message=_(u"There was a problem with creating the item"), errors=category_form.errors, status_code=400)


@app.route('/admin/ic/<ic_id>/category/new', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_new_category})
@load_models(
    (ItemCollection, {'id': 'ic_id'}, 'item_collection'),
    permission='org_admin'
)
def admin_new_category(item_collection):
    return dict(item_collection=item_collection)


def jsonify_edit_category(data_dict):
    category = data_dict['category']
    category_form = CategoryForm(obj=category)
    if request.method == 'GET':
        return jsonify(form_template=render_form(form=category_form, title=u"Edit category", submit=u"Update", with_chrome=False))
    if category_form.validate_on_submit():
        category_form.populate_obj(category)
        db.session.commit()
        return api_success(result={'category': dict(category.current_access())}, doc=_(u"Category was updated"), status_code=201)
    return api_error(message=_(u"There was a problem with updating the category"), errors=category_form.errors, status_code=400)


@app.route('/admin/ic/<ic_id>/category/<category_id>/edit', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_edit_category})
@load_models(
    (Category, {'id': 'category_id'}, 'category'),
    permission='org_admin'
)
def admin_edit_category(category):
    return dict(category=category)
