# -*- coding: utf-8 -*-

from flask import g, Markup, request, flash, url_for, redirect
from coaster.views import load_models
from baseframe import _
from baseframe.forms import render_message, render_redirect, render_form
from ..models import db, Organization
from ..forms import OrgForm, NewOrgForm
from .. import app, lastuser


@lastuser.requires_permission('siteadmin')
@lastuser.requires_login
@app.route('/admin/o/new', methods=['GET', 'POST'])
def new_org():
    # Step 1: Get a list of organizations this user owns
    existing = Organization.query.filter(Organization.userid.in_(g.user.organizations_owned_ids())).all()
    existing_ids = [e.userid for e in existing]
    # Step 2: Prune list to organizations without a profile
    new_orgs = []
    for user_org in g.user.organizations_owned():
        if user_org['userid'] not in existing_ids:
            new_orgs.append((user_org['userid'], user_org['title']))
    if not new_orgs:
        return render_message(
            title=_(u"No organizations found"),
            message=Markup(_(u"You do not have any organizations that are not setup on Boxoffice. "
                u'Would you like to <a href="{link}">create a new organization</a>?').format(
                    link=lastuser.endpoint_url('/organizations/new'))))
    eligible_orgs = []
    for orgid, title in new_orgs:
        eligible_orgs.append((orgid, title))
    if not eligible_orgs:
        return render_message(
            title=_(u"No organizations available"),
            message=_(u"To setup Boxoffice for an organization, you must be the owner of the organization."))

    # Step 3: Ask user to select organization
    form = NewOrgForm()
    form.organization.choices = eligible_orgs
    if request.method == 'GET':
        form.organization.data = new_orgs[0][0]
    if form.validate_on_submit():
        # Step 4: Make a profile
        user_org = [user_org for user_org in g.user.organizations_owned() if user_org['userid'] == form.organization.data][0]
        organization = Organization(name=user_org['name'], title=user_org['title'], userid=user_org['userid'])
        form.populate_obj(organization)
        db.session.add(organization)
        db.session.commit()
        flash(_(u"Created an organization for {org}").format(org=organization.title), "success")
        return redirect(url_for('org', org=organization.name), code=303)
    return render_form(
        form=form,
        title=_(u"Setup Boxoffice for your organization..."),
        submit="Next",
        formid="org_new",
        cancel_url=url_for('index'),
        ajax=False)


@app.route('/admin/o/<name>/edit', methods=['GET', 'POST'])
@load_models(
    (Organization, {'name': 'name'}, 'org'),
    permission='org_admin')
def edit_org(org):
    form = OrgForm(obj=org)
    if form.validate_on_submit():
        form.populate_obj(org)
        db.session.commit()
        flash(_("Your changes have been saved"), 'info')
        return redirect(url_for('org', org=org.name), code=303)
    return render_form(
        form=form,
        title=_("Edit organization settings"),
        submit=_("Save changes"),
        cancel_url='/admin/o/{{org}}'.format(org=org.name),
        ajax=False)
