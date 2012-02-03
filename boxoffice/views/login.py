# -*- coding: utf-8 -*-

from flask import Response, redirect, flash, jsonify
from flask.ext.lastuser import LastUser
from flask.ext.lastuser.sqlalchemy import UserManager
from coaster.views import get_next_url

from boxoffice import app
from boxoffice.models import db, User

lastuser = LastUser(app)
lastuser.init_usermanager(UserManager(db, User))
lastuser.external_resource('invoice/create', 'http://0.0.0.0:6000/invoice/create', 'POST')


@app.route('/login')
@lastuser.login_handler
def login():
    return {'scope': 'id invoice/create'}

@app.route('/test')
@lastuser.requires_login
def test_view():
    return jsonify(lastuser.call_resource('invoice/create'))

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
