#!/usr/bin/env python
from boxoffice import app
from boxoffice.models import *

app.run('0.0.0.0', 6501, debug=True, threaded=True)
