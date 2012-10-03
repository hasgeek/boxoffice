from flask.ext.sqlalchemy import SQLAlchemy
from boxoffice import app
from coaster.sqlalchemy import BaseMixin, BaseNameMixin, BaseScopedNameMixin, BaseScopedIdNameMixin, BaseScopedIdMixin

db = SQLAlchemy(app)

from boxoffice.models.user import *
from boxoffice.models.category import *
from boxoffice.models.event import *
from boxoffice.models.line_item import *
from boxoffice.models.attendee import *
from boxoffice.models.order import *

