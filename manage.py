#!/usr/bin/env python


from boxoffice import app
from boxoffice.models import db
from coaster.manage import init_manager, manager
import boxoffice
import boxoffice.models as models
import boxoffice.views as views


@manager.command
def dbconfig():
    """Show required database configuration."""
    print(  # NOQA: T001
        '''
-- Pipe this into psql as a super user. Example:
-- ./manage.py dbconfig | sudo -u postgres psql boxoffice

CREATE EXTENSION IF NOT EXISTS pg_trgm;
'''
    )


if __name__ == '__main__':
    db.init_app(app)
    manager = init_manager(app, db, boxoffice=boxoffice, models=models, views=views)
    manager.run()
