from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List

from flask import g
import pytz

from flask_lastuser.sqlalchemy import ProfileBase, UserBase2

from . import DynamicMapped, Mapped, Model, db, jsonb_dict, relationship, sa
from .utils import HeadersAndDataTuple

__all__ = ['User', 'Organization']


class User(UserBase2, Model):
    __tablename__ = 'user'

    assignees: Mapped[List[Assignee]] = relationship(
        cascade='all, delete-orphan', back_populates='user'
    )
    orders: Mapped[List[Order]] = relationship(cascade='all, delete-orphan')

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


class Organization(ProfileBase, Model):
    __tablename__ = 'organization'
    __table_args__ = (sa.UniqueConstraint('contact_email'),)

    # The currently used fields in details are address(html) cin (Corporate Identity
    # Number) or llpin (Limited Liability Partnership Identification Number), pan,
    # service_tax_no, support_email, logo (image url), refund_policy (html), ticket_faq
    # (html), website (url)
    details: Mapped[jsonb_dict] = sa.orm.mapped_column()
    contact_email = sa.orm.mapped_column(sa.Unicode(254), nullable=False)
    # This is to allow organizations to have their orders invoiced by the parent
    # organization
    invoicer_id: Mapped[int] = sa.orm.mapped_column(
        sa.ForeignKey('organization.id'), nullable=True
    )
    invoicer: Mapped[Organization] = relationship(
        remote_side='Organization.id',
        back_populates='subsidiaries',
    )
    subsidiaries: DynamicMapped[Organization] = relationship(
        lazy='dynamic',
        cascade='all, delete-orphan',
        back_populates='invoicer',
    )
    item_collections: Mapped[List[ItemCollection]] = relationship(
        cascade='all, delete-orphan', back_populates='organization'
    )

    discount_policies: DynamicMapped[DiscountPolicy] = relationship(
        order_by='DiscountPolicy.created_at.desc()',
        lazy='dynamic',
        cascade='all, delete-orphan',
        back_populates='organization',
    )
    invoices: DynamicMapped[Invoice] = relationship(
        cascade='all, delete-orphan', lazy='dynamic', back_populates='organization'
    )
    orders: DynamicMapped[Order] = relationship(
        cascade='all, delete-orphan', lazy='dynamic', back_populates='organization'
    )

    def permissions(self, actor, inherited=None):
        perms = super().permissions(actor, inherited)
        if self.userid in actor.organizations_owned_ids():
            perms.add('org_admin')
        return perms

    def fetch_invoices(self):
        """Return invoices for an organization as a tuple of (row_headers, rows)."""
        headers = [
            "order_id",
            "receipt_no",
            "invoice_no",
            "status",
            "buyer_taxid",
            "seller_taxid",
            "invoicee_name",
            "invoicee_company",
            "invoicee_email",
            "street_address_1",
            "street_address_2",
            "city",
            "state",
            "state_code",
            "country_code",
            "postcode",
            "invoiced_at",
        ]
        invoices_query = (
            sa.select(
                Order.id,
                Order.invoice_no,
                Invoice.invoice_no,
                Invoice.status,
                Invoice.buyer_taxid,
                Invoice.seller_taxid,
                Invoice.invoicee_name,
                Invoice.invoicee_company,
                Invoice.invoicee_email,
                Invoice.street_address_1,
                Invoice.street_address_2,
                Invoice.city,
                Invoice.state,
                Invoice.state_code,
                Invoice.country_code,
                Invoice.postcode,
                Invoice.invoiced_at,
            )
            .where(Invoice.organization == self)
            .select_from(Invoice)
            .join(Order)
            .order_by(Invoice.invoice_no)
        )
        return HeadersAndDataTuple(
            headers, db.session.execute(invoices_query).fetchall()
        )


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


# Tail imports
from .invoice import Invoice  # isort:skip
from .order import Order  # isort:skip

if TYPE_CHECKING:
    from .discount_policy import DiscountPolicy
    from .item_collection import ItemCollection
    from .line_item import Assignee
