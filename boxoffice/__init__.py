#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Website server for boxoffice.
"""

from flask import Flask
from flaskext.assets import Environment, Bundle
from flaskext.mail import Mail
from coaster import configureapp
from os import environ

# First, make an app and config it

app = Flask(__name__, instance_relative_config=True)
configureapp(app, 'BOXOFFICE_ENV')
mail = Mail()
mail.init_app(app)
assets = Environment(app)

# Second, setup assets

js = Bundle('js/libs/jquery-1.6.4.js',
            'js/libs/jquery.form.js',
            'js/scripts.js',
            filters='jsmin', output='js/packed.js')

assets.register('js_all', js)

# Third, after config, import the models and views

import boxoffice.models
import boxoffice.views
if environ.get('BOXOFFICE_ENV') == 'prod':
    import boxoffice.loghandler

