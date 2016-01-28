# -*- coding: utf-8 -*-
# imports in this file are order-sensitive
import re
from pytz import timezone
from flask import Flask
from flask.ext.assets import Environment, Bundle
from flask.ext.lastuser import Lastuser
from flask.ext.lastuser.sqlalchemy import UserManager
from baseframe import baseframe, baseframe_js, baseframe_css
import coaster.app

app = Flask(__name__, instance_relative_config=True)
lastuser = Lastuser()

assets = Environment(app)
js = Bundle(baseframe_js,
    filters='jsmin', output='js/packed.js')
css = Bundle(baseframe_css, 'css/app.css',
    filters='cssmin', output='css/packed.css')
assets.register('js_all', js)
assets.register('css_all', css)


# Configure the app
def init_for(env):
    coaster.app.init_app(app, env)
    db.init_app(app)
    db.app = app

    lastuser.init_app(app)
    lastuser.init_usermanager(UserManager(boxoffice.models.db, boxoffice.models.User))
    app.config['tz'] = timezone(app.config['TIMEZONE'])

app.register_blueprint(baseframe)
from boxoffice.models import db
import boxoffice.views
