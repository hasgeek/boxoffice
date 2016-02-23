#!/usr/bin/env python

from coaster.manage import init_manager

import boxoffice
import boxoffice.models as models
import boxoffice.views as views
from boxoffice.models import db
from boxoffice import app, init_for


if __name__ == '__main__':
    db.init_app(app)
    manager = init_manager(app, db, init_for, boxoffice=boxoffice, models=models, views=views)

    manager.run()
