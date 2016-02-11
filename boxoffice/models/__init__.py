from flask.ext.sqlalchemy import SQLAlchemy
from boxoffice import app
from coaster.sqlalchemy import BaseMixin, BaseNameMixin, BaseScopedNameMixin, BaseScopedIdNameMixin, BaseScopedIdMixin, IdMixin

from coaster.db import db

from boxoffice.models.user import *
from boxoffice.models.item_collection import *
from boxoffice.models.category import *
from boxoffice.models.item import *
from boxoffice.models.price import *
from boxoffice.models.discount_policy import *
from boxoffice.models.order import *
