# -*- coding: utf-8 -*-

from pytz import timezone
from flask import Flask
from flask_migrate import Migrate
from flask_rq import RQ
from flask_mail import Mail
from flask_lastuser import Lastuser
from flask_lastuser.sqlalchemy import UserManager
from flask_admin import Admin
import wtforms_json
from baseframe import baseframe, assets, Version
from ._version import __version__
import coaster.app


app = Flask(__name__, instance_relative_config=True)
lastuser = Lastuser()

mail = Mail()

# --- Assets ------------------------------------------------------------------

version = Version(__version__)
assets['boxoffice.css'][version] = 'css/app.css'
assets['boxoffice.js'][version] = 'js/scripts.js'


from . import extapi, views  # NOQA
from boxoffice.models import db, User, Item, Price, DiscountPolicy, DiscountCoupon, ItemCollection, Organization, Category, Invoice  # noqa
from siteadmin import OrganizationModelView, DiscountCouponModelView, InvoiceModelView  # noqa


# Configure the app
coaster.app.init_app(app)
db.init_app(app)
db.app = app
migrate = Migrate(app, db)
RQ(app)

lastuser.init_app(app)
lastuser.init_usermanager(UserManager(db, User))
app.config['tz'] = timezone(app.config['TIMEZONE'])
baseframe.init_app(app, requires=['boxoffice'], ext_requires=['baseframe-bs3', 'fontawesome>=4.0.0', 'baseframe-footable', 'jquery.tinymce>=4.0.0'])

mail.init_app(app)
wtforms_json.init()


# This is a temporary solution for an admin interface, only
# to be used until the native admin interface is ready.
try:
    admin = Admin(app, name=u"Boxoffice Admin", template_mode='bootstrap3', url='/siteadmin')
    admin.add_view(OrganizationModelView(Organization, db.session))
    admin.add_view(DiscountCouponModelView(DiscountCoupon, db.session))
    admin.add_view(InvoiceModelView(Invoice, db.session))
except AssertionError:
    pass
