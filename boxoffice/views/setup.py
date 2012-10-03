# -*- coding: utf-8 -*-

"""
Setup Workspace, Create and Manage Items
"""

from flask import flash, url_for, render_template, g
from coaster.views import load_model, load_models
from coaster import format_currency as coaster_format_currency
from baseframe.forms import render_form, render_redirect, render_delete_sqla, render_message
from flask.ext.wtf import SelectField, Required
from flask import session

from boxoffice import app
from boxoffice.models import db
from boxoffice.views.login import lastuser, requires_workspace_member, requires_workspace_owner

from boxoffice.models.category import Category, CATEGORY_STATUS
from boxoffice.models.event import Event
from boxoffice.models.order import Order, HALF_DOZEN
from boxoffice.models.line_item import LineItem

from boxoffice.forms.category import CategoryForm
from boxoffice.forms.event import EventForm
from boxoffice.forms.attendee import AttendeeForm, SelectTicketsForm, RegistrationForm

@app.template_filter('format_currency')
def format_currency(value):
    return coaster_format_currency(value, decimals=2)

@app.route('/new', methods=['GET', 'POST'])
@lastuser.requires_login
def event_new():
    form = EventForm()
    if form.validate_on_submit():
        event = Event(title=form.title.data, description=form.description.data, venue=form.venue.data,
            short_venue=form.short_venue.data, funnel_link=form.funnel_link.data,
         website=form.website.data,date=form.date.data,
         contact_name=form.contact_name.data,contact_email=form.contact_email.data)
        event.make_name()
        db.session.add(event)
        db.session.commit()
        flash("Created new event for %s" % Event.title, "success")
        return render_redirect(url_for('event_view', event=event.name), code=303)
    return render_form(form=form, title="Create a new event", submit="Create",
        formid="event_new", cancel_url=url_for('index'), ajax=False)

@app.route('/<event>/edit', methods=['GET', 'POST'])
@load_model(Event, {'name': 'event'}, 'event')
@lastuser.requires_login
def event_edit(event):
    form = EventForm(obj=event)
    if form.validate_on_submit():
        form.populate_obj(event)
        db.session.add(event)
        db.session.commit()
        flash("Saved event %s" % event.title, "success")
        return render_redirect(url_for('event_view', event=event.name), code=303)
    return render_form(form=form, title="Edit Event", submit="Save",
        formid="event_edit", cancel_url=url_for('event_view', event=event.name), ajax=False)


def nonzero_ticket_check(form):
    for field in form:
        print "FIELD:", field.name , "DATA:", field.data
        if 'csrf_token' not in field.name and field.data != 0:
            return True
    flash("Please select at least one ticket.", "error")
    return False


@app.route('/<event>/', methods=['GET', 'POST'])
@load_model(Event, {'name': 'event'}, 'event')
@lastuser.requires_login
def event_view(event):
    categories = Category.get_by_event(event=event)
    live_categories = Category.get_by_event_and_status(event=event, status=CATEGORY_STATUS.LIVE)
    field = SelectField(choices=HALF_DOZEN, coerce=int)
    for c in categories:
        setattr(SelectTicketsForm, c.name, field)
    form = SelectTicketsForm()
    if form.is_submitted() and nonzero_ticket_check(form):
        order = Order(user=g.user)
        for field in form:
            if field.name != 'csrf_token' and field.data:
                print "VALIDATED FIELD:", field.name, "DATA:", field.data
                category = Category.query.filter_by(event=event, name=field.name).first()
                lineitem = LineItem(order=order, category=category, quantity=field.data)
                db.session.add(lineitem)
                db.session.commit()
                lineitem.update_total()
                order.update_total()
                db.session.commit()
                print "LINE ITEM:", lineitem.category.event.title, ":", lineitem.category.title, "(",lineitem.quantity,")"
                print "ORDER TOTAL:", order.total
        session['order'] = order.id
        return render_redirect(url_for('registration'), code=303)
    return render_template('event.html', event=event, categories=categories, live_categories=live_categories, form=form)


@app.route('/<event>/categories/new', methods=['GET', 'POST'])
@load_model(Event, {'name': 'event'}, 'event')
@lastuser.requires_login
def category_new(event):
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(event=event)
        form.populate_obj(category)
        category.make_name()
        db.session.add(category)
        db.session.commit()
        flash("Created new category in Event '%s'." % event.name, "success")
        return render_redirect(url_for('event_view', event=event.name), code=303)
    return render_form(form=form, title=event.title + u" - New Ticket Category",
        formid="category_new", submit=u"Create",
        cancel_url=url_for('event_view', event=event.name), ajax=False)


@app.route('/<event>/categories/<category>/edit', methods=['GET', 'POST'])
@load_models(
    (Event, {'name': 'event'}, 'event'),
    (Category, {'name': 'category', 'event': 'event'}, 'category')
    )
@lastuser.requires_login
def category_edit(event, category):
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        form.populate_obj(category)
        category.make_name()
        db.session.commit()
        flash("Edited item '%s'" % category.name, "success")
        return render_redirect(url_for('event_view', event=event.name), code=303)
    return render_form(form=form, title=u"Edit Category",
        formid='category_edit', submit=u"Save",
        cancel_url=url_for('event_view', event=event.name), ajax=True)

@app.route('/<event>/categories/<category>/delete', methods=['GET', 'POST'])
@load_models(
    (Event, {'name': 'event'}, 'event'),
    (Category, {'name': 'category', 'event': 'event'}, 'category')
    )
@lastuser.requires_login
def category_delete(event, category):
    return render_delete_sqla(category, db, title=u"Confirm delete",
        message=u"Delete Category '%s'?" % category.title,
        success=u"You have deleted category '%s'." % category.title,
        next=url_for('event_view', event=event.name))

