# -*- coding: utf-8 -*-

from datetime import datetime
import pytz
import six
from flask import g
from flask_lastuser.sqlalchemy import UserBase2, ProfileBase
from boxoffice.models import db, JsonDict


__all__ = ['User', 'Organization']


class User(UserBase2, db.Model):

    __tablename__ = 'user'

    def __repr__(self):
        return self.fullname

    @property
    def orgs(self):
        return Organization.query.filter(Organization.userid.in_(self.organizations_owned_ids()))


def default_user(context):
    return g.user.id if g.user else None


def naive_to_utc(dt, timezone=None):
    """
    Returns a UTC datetime for a given naive datetime or date object
    Localizes it to the given timezone and converts it into a UTC datetime
    """
    if timezone:
        if isinstance(timezone, six.string_types):
            tz = pytz.timezone(timezone)
        else:
            tz = timezone
    elif isinstance(dt, datetime) and dt.tzinfo:
        tz = dt.tzinfo
    else:
        tz = pytz.UTC

    return tz.localize(dt).astimezone(tz).astimezone(pytz.UTC)


class Organization(ProfileBase, db.Model):
    __tablename__ = 'organization'
    __table_args__ = (db.UniqueConstraint('contact_email'),
        db.CheckConstraint('fy_start_month >= 1 and fy_start_month <= 12', 'org_month_check'),
        db.CheckConstraint('fy_start_day >= 1 and fy_start_month <= 31', 'org_day_check'))

    # The currently used fields in details are address(html), cin (Corporate Identity Number)
    # pan service_tax_no, support_email,
    # logo (image url), refund_policy (html), ticket_faq (html), website (url)
    details = db.Column(JsonDict, nullable=False, server_default='{}')
    contact_email = db.Column(db.Unicode(254), nullable=False)
    fy_start_month = db.Column(db.Integer, nullable=True)
    fy_start_day = db.Column(db.Integer, nullable=True)
    # Eg: Asia/Kolkata
    fy_timezone = db.Column(db.Unicode(255), nullable=True)

    @property
    def fy_start_at(self):
        if not self.fy_start_month or not self.fy_start_day or not self.fy_timezone:
            return None
        current_year = datetime.utcnow().year
        fy_start_at = naive_to_utc(datetime(current_year, self.fy_start_month, self.fy_start_day), self.fy_timezone)
        if naive_to_utc(datetime.utcnow()) < fy_start_at:
            # Consider a case where the current date is 2017-01-01
            # and the financial start month/date is 4/1. In that case, the current fy_start_at 
            # should be 2016-04-01, hence a year is subtracted from the current datetime
            fy_start_at = naive_to_utc(datetime(current_year - 1, self.fy_start_month, self.fy_start_day), self.fy_timezone)
        return fy_start_at

    def permissions(self, user, inherited=None):
        perms = super(Organization, self).permissions(user, inherited)
        if self.userid in user.organizations_owned_ids():
            perms.add('org_admin')
        return perms
