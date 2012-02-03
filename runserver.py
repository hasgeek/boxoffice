#!/usr/bin/env python

from boxoffice import app
from boxoffice.models import db
from os import environ

environ['BOXOFFICE_ENV'] = 'dev'

db.create_all()
app.config['ASSETS_DEBUG'] = True
app.run('0.0.0.0', 6500, debug=True)
