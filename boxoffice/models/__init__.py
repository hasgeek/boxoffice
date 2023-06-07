# flake8: noqa

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy_json import mutable_json_type
from typing_extensions import Annotated, TypeAlias
import sqlalchemy as sa

from coaster.sqlalchemy import (
    AppenderQuery,
    BaseMixin,
    BaseNameMixin,
    BaseScopedIdMixin,
    BaseScopedIdNameMixin,
    BaseScopedNameMixin,
    DynamicMapped,
    IdMixin,
    MarkdownColumn,
    ModelBase,
    Query,
    TimestampMixin,
    UuidMixin,
    relationship,
)


class Model(ModelBase, DeclarativeBase):
    """Base for all models."""

    __with_timezone__ = True


timestamptz: TypeAlias = Annotated[
    datetime, sa.orm.mapped_column(sa.TIMESTAMP(timezone=True))
]
timestamptz_now: TypeAlias = Annotated[
    datetime,
    sa.orm.mapped_column(sa.TIMESTAMP(timezone=True), default=sa.func.utcnow()),
]
jsonb: TypeAlias = Annotated[
    dict,
    sa.orm.mapped_column(
        # FIXME: mutable_json_type assumes `dict|list`, not just `dict`
        mutable_json_type(
            dbtype=sa.JSON().with_variant(postgresql.JSONB, 'postgresql'), nested=True
        )
    ),
]
jsonb_dict: TypeAlias = Annotated[
    dict,
    sa.orm.mapped_column(
        # FIXME: mutable_json_type assumes `dict|list`, not just `dict`
        mutable_json_type(
            dbtype=sa.JSON().with_variant(postgresql.JSONB, 'postgresql'), nested=True
        ),
        nullable=False,
        server_default=sa.text("'{}'::jsonb"),
    ),
]


TimestampMixin.__with_timezone__ = True
db = SQLAlchemy(metadata=Model.metadata, query_class=Query)  # type: ignore[arg-type]
Model.init_flask_sqlalchemy(db)

from .enums import *  # isort:skip
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
