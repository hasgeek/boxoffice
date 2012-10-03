# -*- coding: utf-8 -*-

from functools import wraps

from flask import g, Response, redirect, flash, url_for, request, abort
from flask.ext.lastuser import LastUser
from flask.ext.lastuser.sqlalchemy import UserManager
from coaster.views import get_next_url

from boxoffice import app, lastuser
from boxoffice.models import db, User

lastuser.init_usermanager(UserManager(db, User))


@app.route('/login')
@lastuser.login_handler
def login():
    return {'scope': 'id email organizations invoice invoice/new'}


@app.route('/logout')
@lastuser.logout_handler
def logout():
    flash(u"You are now logged out", category='info')
    return get_next_url()


@app.route('/login/redirect')
@lastuser.auth_handler
def lastuserauth():
    # Save the user object
    db.session.commit()
    return redirect(get_next_url())


@lastuser.auth_error_handler
def lastuser_error(error, error_description=None, error_uri=None):
    if error == 'access_denied':
        flash("You denied the request to login", category='error')
        return redirect(get_next_url())
    return Response(u"Error: %s\n"
                    u"Description: %s\n"
                    u"URI: %s" % (error, error_description, error_uri),
                    mimetype="text/plain")


def requires_workspace_member(f):
    """
    Decorator that checks if the current user is a member of the organization
    associated with the current workspace. This decorator must be applied
    before load_model (ie, below load_model in code order) and expects a
    "workspace" parameter that refers to a Workspace model instance. The
    function does not require an additional lastuser.requires_login wrapper.
    The workspace is also posted as g.workspace for general access.
    """
    @wraps(f)
    def decorated_function(workspace, *args, **kwargs):
        if not g.user:
            return redirect(url_for('login', next=url_for(request.endpoint, **request.view_args)))
        if workspace.userid not in g.user.organizations_memberof_ids():
            abort(403)
        g.workspace = workspace
        return f(workspace=workspace, *args, **kwargs)
    return decorated_function


def requires_workspace_owner(f):
    """
    Decorator that checks if the current user is a member of the organization
    associated with the current workspace. This decorator must be applied
    before load_model (ie, below load_model in code order) and expects a
    "workspace" parameter that refers to a Workspace model instance. The
    function does not require an additional lastuser.requires_login wrapper.
    The workspace is also posted as g.workspace for general access.
    """
    @wraps(f)
    def decorated_function(workspace, *args, **kwargs):
        if not g.user:
            return redirect(url_for('login', next=url_for(request.endpoint, **request.view_args)))
        if workspace.userid not in g.user.organizations_owned_ids():
            abort(403)
        g.workspace = workspace
        return f(workspace=workspace, *args, **kwargs)
    return decorated_function
