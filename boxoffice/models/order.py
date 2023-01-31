from collections import namedtuple
from decimal import Decimal

from sqlalchemy.sql import func, select

from baseframe import __
from coaster.utils import LabeledEnum, buid, utcnow

from . import BaseMixin, db
from .user import User

__all__ = ['Order', 'ORDER_STATUS', 'OrderSession']

OrderAmounts = namedtuple(
    'OrderAmounts',
    ['base_amount', 'discounted_amount', 'final_amount', 'confirmed_amount'],
)


class ORDER_STATUS(LabeledEnum):  # NOQA: N801
    PURCHASE_ORDER = (0, __("Purchase Order"))
    SALES_ORDER = (1, __("Sales Order"))
    INVOICE = (2, __("Invoice"))
    CANCELLED = (3, __("Cancelled Order"))

    CONFIRMED = {SALES_ORDER, INVOICE}
    TRANSACTION = {SALES_ORDER, INVOICE, CANCELLED}


def gen_invoice_no(organization):
    """Generate a sequential invoice number for an order, given an organization."""
    return (
        select(func.coalesce(func.max(Order.invoice_no + 1), 1))
        .where(Order.organization == organization)
        .scalar_subquery()
    )


class Order(BaseMixin, db.Model):
    __tablename__ = 'customer_order'
    __uuid_primary_key__ = True
    __table_args__ = (
        db.UniqueConstraint('organization_id', 'invoice_no'),
        db.UniqueConstraint('access_token'),
    )

    user_id = db.Column(None, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship(
        User, backref=db.backref('orders', cascade='all, delete-orphan')
    )
    item_collection_id = db.Column(
        None, db.ForeignKey('item_collection.id'), nullable=False
    )
    item_collection = db.relationship(
        'ItemCollection',
        backref=db.backref('orders', cascade='all, delete-orphan', lazy='dynamic'),
    )

    organization_id = db.Column(None, db.ForeignKey('organization.id'), nullable=False)
    organization = db.relationship(
        'Organization',
        backref=db.backref('orders', cascade='all, delete-orphan', lazy='dynamic'),
    )

    status = db.Column(db.Integer, default=ORDER_STATUS.PURCHASE_ORDER, nullable=False)

    initiated_at = db.Column(
        db.TIMESTAMP(timezone=True), nullable=False, default=db.func.utcnow()
    )
    paid_at = db.Column(db.TIMESTAMP(timezone=True), nullable=True)
    invoiced_at = db.Column(db.TIMESTAMP(timezone=True), nullable=True)
    cancelled_at = db.Column(db.TIMESTAMP(timezone=True), nullable=True)

    access_token = db.Column(db.Unicode(22), nullable=False, default=buid)

    buyer_email = db.Column(db.Unicode(254), nullable=False)
    buyer_fullname = db.Column(db.Unicode(80), nullable=False)
    buyer_phone = db.Column(db.Unicode(16), nullable=False)

    # TODO: Deprecate invoice_no, rename to receipt_no instead
    invoice_no = db.Column(db.Integer, nullable=True)
    receipt_no = db.synonym('invoice_no')

    # These 3 properties are defined below the LineItem model -
    # confirmed_line_items, initial_line_items, confirmed_and_cancelled_line_items

    def permissions(self, user, inherited=None):
        perms = super(Order, self).permissions(user, inherited)
        if self.organization.userid in user.organizations_owned_ids():
            perms.add('org_admin')
        return perms

    def confirm_sale(self):
        """Update the status to ORDER_STATUS.SALES_ORDER."""
        for line_item in self.line_items:
            line_item.confirm()
        self.invoice_no = gen_invoice_no(self.organization)
        self.status = ORDER_STATUS.SALES_ORDER
        self.paid_at = utcnow()

    def invoice(self):
        """Set invoiced_at and status."""
        for line_item in self.line_items:
            line_item.confirm()
        self.invoiced_at = utcnow()
        self.status = ORDER_STATUS.INVOICE

    def get_amounts(self, line_item_status):
        """Calculate and return the order's amounts as an OrderAmounts tuple."""
        base_amount = Decimal(0)
        discounted_amount = Decimal(0)
        final_amount = Decimal(0)
        confirmed_amount = Decimal(0)
        for line_item in self.line_items:
            if line_item.status == line_item_status:
                base_amount += line_item.base_amount
                discounted_amount += line_item.discounted_amount
                final_amount += line_item.final_amount
            if line_item.is_confirmed:
                confirmed_amount += line_item.final_amount
        return OrderAmounts(
            base_amount, discounted_amount, final_amount, confirmed_amount
        )

    @property
    def is_confirmed(self):
        return self.status in ORDER_STATUS.CONFIRMED

    def is_fully_assigned(self):
        """Check if all the line items in an order have an assignee."""
        for line_item in self.get_confirmed_line_items:
            if not line_item.current_assignee:
                return False
        return True


class OrderSession(BaseMixin, db.Model):
    """Records the referrer and utm headers for an order."""

    __tablename__ = 'order_session'
    __uuid_primary_key__ = True

    customer_order_id = db.Column(
        None,
        db.ForeignKey('customer_order.id'),
        nullable=False,
        index=True,
        unique=False,
    )
    order = db.relationship(
        Order,
        backref=db.backref('session', cascade='all, delete-orphan', uselist=False),
    )

    referrer = db.Column(db.Unicode(2083), nullable=True)
    host = db.Column(db.UnicodeText, nullable=True)

    # Google Analytics parameters
    utm_source = db.Column(db.Unicode(250), nullable=False, default='', index=True)
    utm_medium = db.Column(db.Unicode(250), nullable=False, default='', index=True)
    utm_term = db.Column(db.Unicode(250), nullable=False, default='')
    utm_content = db.Column(db.Unicode(250), nullable=False, default='')
    utm_id = db.Column(db.Unicode(250), nullable=False, default='', index=True)
    utm_campaign = db.Column(db.Unicode(250), nullable=False, default='', index=True)
    # Google click id (for AdWords)
    gclid = db.Column(db.Unicode(250), nullable=False, default='', index=True)
