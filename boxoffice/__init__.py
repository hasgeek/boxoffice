"""Initialize Boxoffice."""

from decimal import Decimal
from typing import Any

from flask import Flask
from flask_mail import Mail
from flask_migrate import Migrate
from flask_rq2 import RQ
from pytz import timezone

import coaster.app
from baseframe import Version, baseframe
from baseframe.utils import JSONProvider
from coaster.assets import WebpackManifest
from flask_lastuser import Lastuser
from flask_lastuser.sqlalchemy import UserManager

from ._version import __version__

app = Flask(__name__, instance_relative_config=True)
lastuser = Lastuser()

mail = Mail()
rq = RQ()
webpack = WebpackManifest(
    app, filepath='static/build/manifest.json', jinja_global='webpack'
)

# --- Assets ---------------------------------------------------------------------------

version = Version(__version__)

# --- Import rest of the app -----------------------------------------------------------

from . import cli, extapi, views  # NOQA  # isort:skip
from .models import (  # NOQA  # isort:skip
    Category,
    DiscountCoupon,
    DiscountPolicy,
    Invoice,
    Ticket,
    Menu,
    Organization,
    Price,
    User,
    db,
)

# --- Handle JSON quirk for Boxoffice --------------------------------------------------


class DecimalJsonProvider(JSONProvider):
    """Custom JSON provider that converts Decimal to float."""

    # Required until Boxoffice JS recognises currency represented as numeric strings
    @staticmethod
    def default(o: Any) -> Any:
        if isinstance(o, Decimal):
            return float(o)
        return JSONProvider.default(o)


# --- Configure ------------------------------------------------------------------------

coaster.app.init_app(app, ['py', 'env'], env_prefix=['FLASK', 'APP_BOXOFFICE'])
db.init_app(app)
migrate = Migrate(app, db)
rq.init_app(app)

lastuser.init_app(app)
lastuser.init_usermanager(UserManager(db, User))
app.config['tz'] = timezone(app.config['TIMEZONE'])
baseframe.init_app(
    app,
    requires=['boxoffice'],
    ext_requires=[
        'baseframe-bs3',
        'fontawesome>=4.0.0',
        'baseframe-footable',
        'jquery.tinymce>=4.0.0',
        'codemirror-json',
    ],
)
app.json = DecimalJsonProvider(app)
app.jinja_env.policies['json.dumps_function'] = app.json.dumps

mail.init_app(app)
