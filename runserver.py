#!/usr/bin/env python
from boxoffice import app, init_for
from boxoffice.models import db
init_for('dev')
db.create_all()
app.run('0.0.0.0', 6500, debug=True)
