from flaskext.sqlalchemy import SQLAlchemy
from boxoffice import app
from coaster.sqlalchemy import BaseMixin, BaseNameMixin

db = SQLAlchemy(app)

from boxoffice.models.user import *
