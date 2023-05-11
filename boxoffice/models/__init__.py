# flake8: noqa

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped
import sqlalchemy as sa

from coaster.sqlalchemy import (
    BaseMixin,
    BaseNameMixin,
    BaseScopedIdMixin,
    BaseScopedIdNameMixin,
    BaseScopedNameMixin,
    IdMixin,
    JsonDict,
    MarkdownColumn,
    TimestampMixin,
    UuidMixin,
)

TimestampMixin.__with_timezone__ = True
db = SQLAlchemy()

from .category import *  # isort:skip
from .discount_policy import *  # isort:skip
from .invoice import *  # isort:skip
from .item import *  # isort:skip
from .item_collection import *  # isort:skip
from .line_item import *  # isort:skip
from .line_item_discounter import *  # isort:skip
from .order import *  # isort:skip
from .payment import *  # isort:skip
from .user import *  # isort:skip
from .utils import *  # isort:skip
