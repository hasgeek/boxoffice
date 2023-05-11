from __future__ import annotations

from datetime import datetime

from flask import g

import pytz

from flask_lastuser.sqlalchemy import ProfileBase, UserBase2

from . import JsonDict, Mapped, db, sa

__all__ = ['User', 'Organization']


class User(UserBase2, db.Model):  # type: ignore[name-defined]
    __tablename__ = 'user'

    def __repr__(self):
        """Return a representation."""
        return self.fullname

    @property
    def orgs(self):
        return Organization.query.filter(
            Organization.userid.in_(self.organizations_owned_ids())
        )


def default_user(context):
    return g.user.id if g.user else None


def naive_to_utc(dt, timezone=None):
    """
    Return a UTC datetime for a given naive datetime or date object.

    Localizes it to the given timezone and converts it into a UTC datetime
    """
    if timezone:
        if isinstance(timezone, str):
            tz = pytz.timezone(timezone)
        else:
            tz = timezone
    elif isinstance(dt, datetime) and dt.tzinfo:
        tz = dt.tzinfo
    else:
        tz = pytz.UTC

    return tz.localize(dt).astimezone(tz).astimezone(pytz.UTC)


class Organization(ProfileBase, db.Model):  # type: ignore[name-defined]
    __tablename__ = 'organization'
    __table_args__ = (sa.UniqueConstraint('contact_email'),)

    # The currently used fields in details are address(html)
    # cin (Corporate Identity Number) or llpin (Limited Liability Partnership Identification Number),
    # pan, service_tax_no, support_email,
    # logo (image url), refund_policy (html), ticket_faq (html), website (url)
    details: Mapped[dict] = sa.orm.mapped_column(
        JsonDict, nullable=False, server_default='{}'
    )
    contact_email = sa.Column(sa.Unicode(254), nullable=False)
    # This is to allow organizations to have their orders invoiced by the parent organization
    invoicer_id: Mapped[int] = sa.orm.mapped_column(
        sa.ForeignKey('organization.id'), nullable=True
    )
    invoicer = sa.orm.relationship(
        'Organization',
        remote_side='Organization.id',
        backref=sa.orm.backref(
            'subsidiaries', cascade='all, delete-orphan', lazy='dynamic'
        ),
    )

    def permissions(self, user, inherited=None):
        perms = super().permissions(user, inherited)
        if self.userid in user.organizations_owned_ids():
            perms.add('org_admin')
        return perms


def get_fiscal_year(jurisdiction, dt):
    """
    Return the financial year for a given jurisdiction and timestamp.

    Returns start and end dates as tuple of timestamps. Recognizes April 1 as the start
    date for India (jurisfiction code: 'in'), January 1 everywhere else.

    Example::

        get_fiscal_year('IN', utcnow())
    """
    if jurisdiction.lower() == 'in':
        if dt.month < 4:
            start_year = dt.year - 1
        else:
            start_year = dt.year
        # starts on April 1 XXXX
        fy_start = datetime(start_year, 4, 1)
        # ends on April 1 XXXX + 1
        fy_end = datetime(start_year + 1, 4, 1)
        timezone = 'Asia/Kolkata'
        return (naive_to_utc(fy_start, timezone), naive_to_utc(fy_end, timezone))
    return (
        naive_to_utc(datetime(dt.year, 1, 1)),
        naive_to_utc(datetime(dt.year + 1, 1, 1)),
    )
