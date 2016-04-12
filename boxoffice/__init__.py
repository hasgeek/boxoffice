# -*- coding: utf-8 -*-
# imports in this file are order-sensitive
from pytz import timezone
from flask import Flask
from flask.ext.mail import Mail
from flask.ext.lastuser import Lastuser
from flask.ext.lastuser.sqlalchemy import UserManager
from baseframe import baseframe, assets, Version
from ._version import __version__
import coaster.app
import wtforms_json


app = Flask(__name__, instance_relative_config=True)
lastuser = Lastuser()

mail = Mail()

# --- Assets ------------------------------------------------------------------

version = Version(__version__)
assets['boxoffice.js'][version] = 'js/scripts.js'
assets['boxoffice.css'][version] = 'css/order.css'


from boxoffice.models import db, User  # noqa
from . import extapi, views  # noqa


# Configure the app
def init_for(env):
    coaster.app.init_app(app, env)
    db.init_app(app)
    db.app = app

    lastuser.init_app(app)
    lastuser.init_usermanager(UserManager(db, User))
    app.config['tz'] = timezone(app.config['TIMEZONE'])

    baseframe.init_app(app, requires=['boxoffice'], ext_requires=['baseframe-bs3', 'fontawesome>=4.0.0', 'ractive', 'ractive-transitions-fly', 'validate'])

    mail.init_app(app)
    wtforms_json.init()
