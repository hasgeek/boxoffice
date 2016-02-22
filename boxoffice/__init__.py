# -*- coding: utf-8 -*-
# imports in this file are order-sensitive
from pytz import timezone
from flask import Flask
from flask.ext.mail import Mail
from flask.ext.lastuser import Lastuser
from flask.ext.lastuser.sqlalchemy import UserManager
import coaster.app
import wtforms_json


app = Flask(__name__, instance_relative_config=True)
lastuser = Lastuser()
ALLOWED_ORIGINS = ['http://shreyas-wlan.dev:8000',
                   'http://rootconf.vidya.dev:8090',
                   'http://rootconf.karthik.dev:8090']

mail = Mail()


from boxoffice.models import db  # noqa
import boxoffice.views  # noqa


# Configure the app
def init_for(env):
    coaster.app.init_app(app, env)
    db.init_app(app)
    db.app = app

    lastuser.init_app(app)
    lastuser.init_usermanager(UserManager(boxoffice.models.db,
                                          boxoffice.models.User))
    app.config['tz'] = timezone(app.config['TIMEZONE'])

    mail.init_app(app)
    wtforms_json.init()
