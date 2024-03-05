from flask import flash, redirect
from markupsafe import Markup, escape

from baseframe import _
from baseframe.forms import render_message
from coaster.views import get_next_url

from .. import app, lastuser
from ..models import User, db


@app.route('/login')
@lastuser.login_handler
def login():
    return {'scope': 'id email phone organizations'}


@app.route('/logout')
@lastuser.logout_handler
def logout():
    flash(_("You are now logged out"), category='success')
    return get_next_url()


@app.route('/login/redirect')
@lastuser.auth_handler
def lastuserauth():
    return redirect(get_next_url())


@app.route('/login/notify', methods=['POST'])
@lastuser.notification_handler
def lastusernotify(_user: User) -> None:
    # Perform operations here if required.
    # Warning: this *could* be a spoof call, so ignore all request data.
    # Only trust the 'user' parameter to this function.
    db.session.commit()


@lastuser.auth_error_handler
def lastuser_error(error, error_description=None, error_uri=None):
    if error == 'access_denied':
        flash(_("You denied the request to login"), category='error')
        return redirect(get_next_url())
    return render_message(
        title=_("Error: {error}").format(error=error),
        message=Markup(
            f'<p>{escape(error_description or "")}</p>'
            f'<p>URI: {escape(error_uri or _("NA"))}</p>'
        ),
    )
