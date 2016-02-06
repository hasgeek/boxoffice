#!/usr/bin/env python
from boxoffice import app, init_for, models
from boxoffice.models import *
init_for('dev')

app.run('0.0.0.0', 6500, debug=True)
