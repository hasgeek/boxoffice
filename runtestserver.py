#!/usr/bin/env python
from boxoffice import app, init_for, db
from boxoffice.models import *
from tests import init_data


init_for('testing')
db.drop_all()
db.create_all()
init_data()

app.run('0.0.0.0', 6500, debug=True)
