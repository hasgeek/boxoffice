from __future__ import annotations

from collections import namedtuple
from decimal import Decimal
from typing import TYPE_CHECKING, List
from uuid import UUID, uuid4

from sqlalchemy.ext.orderinglist import ordering_list

from coaster.utils import buid, utcnow

from . import AppenderQuery, BaseMixin, DynamicMapped, Mapped, Model, relationship, sa
from .enums import LINE_ITEM_STATUS, ORDER_STATUS, TRANSACTION_TYPE
from .line_item import LineItem

__all__ = ['Order', 'OrderSession']

OrderAmounts = namedtuple(
    'OrderAmounts',
    ['base_amount', 'discounted_amount', 'final_amount', 'confirmed_amount'],
)


def gen_invoice_no(organization):
    """Generate a sequential invoice number for an order, given an organization."""
    return (
        sa.select(sa.func.coalesce(sa.func.max(Order.invoice_no + 1), 1))
        .where(Order.organization == organization)
        .scalar_subquery()
    )


class Order(BaseMixin, Model):
    __tablename__ = 'customer_order'
    __uuid_primary_key__ = True
    __table_args__ = (
        sa.UniqueConstraint('organization_id', 'invoice_no'),
        sa.UniqueConstraint('access_token'),
    )

    id: Mapped[UUID] = sa.orm.mapped_column(  # type: ignore[assignment]  # noqa: A003
        primary_key=True, default=uuid4
    )
    user_id: Mapped[int] = sa.orm.mapped_column(sa.ForeignKey('user.id'), nullable=True)
    user: Mapped[User] = relationship(back_populates='orders')
    item_collection_id: Mapped[UUID] = sa.orm.mapped_column(
        sa.ForeignKey('item_collection.id'), nullable=False
    )
    item_collection: Mapped[ItemCollection] = relationship(back_populates='orders')

    organization_id: Mapped[int] = sa.orm.mapped_column(
        sa.ForeignKey('organization.id'), nullable=False
    )
    organization: Mapped[Organization] = relationship(back_populates='orders')

    status = sa.orm.mapped_column(
        sa.Integer, default=ORDER_STATUS.PURCHASE_ORDER, nullable=False
    )

    initiated_at = sa.orm.mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, default=sa.func.utcnow()
    )
    paid_at = sa.orm.mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    invoiced_at = sa.orm.mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    cancelled_at = sa.orm.mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)

    access_token = sa.orm.mapped_column(sa.Unicode(22), nullable=False, default=buid)

    buyer_email = sa.orm.mapped_column(sa.Unicode(254), nullable=False)
    buyer_fullname = sa.orm.mapped_column(sa.Unicode(80), nullable=False)
    buyer_phone = sa.orm.mapped_column(sa.Unicode(16), nullable=False)

    # TODO: Deprecate invoice_no, rename to receipt_no instead
    invoice_no = sa.orm.mapped_column(sa.Integer, nullable=True)
    receipt_no = sa.orm.synonym('invoice_no')

    line_items: Mapped[List[LineItem]] = relationship(
        cascade='all, delete-orphan',
        order_by='LineItem.line_item_seq',
        collection_class=ordering_list('line_item_seq', count_from=1),
        back_populates='order',
    )
    session: Mapped[OrderSession] = relationship(
        cascade='all, delete-orphan', uselist=False, back_populates='order'
    )
    online_payments: Mapped[List[OnlinePayment]] = relationship(
        cascade='all, delete-orphan'
    )
    transactions: DynamicMapped[PaymentTransaction] = relationship(
        cascade='all, delete-orphan', lazy='dynamic', back_populates='order'
    )
    invoices: Mapped[List[Invoice]] = relationship(
        cascade='all, delete-orphan', back_populates='order'
    )

    confirmed_line_items: DynamicMapped[LineItem] = relationship(
        lazy='dynamic',
        primaryjoin=sa.and_(
            LineItem.customer_order_id == id,
            LineItem.status == LINE_ITEM_STATUS.CONFIRMED,
        ),
        viewonly=True,
    )

    confirmed_and_cancelled_line_items: DynamicMapped[LineItem] = relationship(
        lazy='dynamic',
        primaryjoin=sa.and_(
            LineItem.customer_order_id == id,
            LineItem.status.in_(
                [LINE_ITEM_STATUS.CONFIRMED, LINE_ITEM_STATUS.CANCELLED]
            ),
        ),
        viewonly=True,
    )

    initial_line_items: DynamicMapped[LineItem] = relationship(
        lazy='dynamic',
        primaryjoin=sa.and_(
            LineItem.customer_order_id == id,
            LineItem.previous_id.is_(None),
            LineItem.status.in_(LINE_ITEM_STATUS.TRANSACTION),
        ),
        viewonly=True,
    )

    # These 3 properties are defined below the LineItem model -
    # confirmed_line_items, initial_line_items, confirmed_and_cancelled_line_items

    def permissions(self, actor, inherited=None):
        perms = super().permissions(actor, inherited)
        if self.organization.userid in actor.organizations_owned_ids():
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
    def is_confirmed(self) -> bool:
        return self.status in ORDER_STATUS.CONFIRMED

    def is_fully_assigned(self) -> bool:
        """Check if all the line items in an order have an assignee."""
        for line_item in self.confirmed_line_items:
            if not line_item.current_assignee:
                return False
        return True

    @property
    def refund_transactions(self) -> AppenderQuery[PaymentTransaction]:
        return self.transactions.filter_by(transaction_type=TRANSACTION_TYPE.REFUND)

    @property
    def payment_transactions(self) -> AppenderQuery[PaymentTransaction]:
        return self.transactions.filter_by(transaction_type=TRANSACTION_TYPE.PAYMENT)

    @property
    def paid_amount(self) -> Decimal:
        return sum(
            (
                order_transaction.amount
                for order_transaction in self.payment_transactions
            ),
            Decimal(),
        )

    @property
    def refunded_amount(self) -> Decimal:
        return sum(
            (
                order_transaction.amount
                for order_transaction in self.refund_transactions
            ),
            Decimal(),
        )

    @property
    def net_amount(self) -> Decimal:
        return self.paid_amount - self.refunded_amount


class OrderSession(BaseMixin, Model):
    """Records the referrer and utm headers for an order."""

    __tablename__ = 'order_session'
    __uuid_primary_key__ = True

    customer_order_id: Mapped[UUID] = sa.orm.mapped_column(
        sa.ForeignKey('customer_order.id'), nullable=False, index=True, unique=False
    )
    order: Mapped[Order] = relationship(back_populates='session')

    referrer = sa.orm.mapped_column(sa.Unicode(2083), nullable=True)
    host = sa.orm.mapped_column(sa.UnicodeText, nullable=True)

    # Google Analytics parameters
    utm_source = sa.orm.mapped_column(
        sa.Unicode(250), nullable=False, default='', index=True
    )
    utm_medium = sa.orm.mapped_column(
        sa.Unicode(250), nullable=False, default='', index=True
    )
    utm_term = sa.orm.mapped_column(sa.Unicode(250), nullable=False, default='')
    utm_content = sa.orm.mapped_column(sa.Unicode(250), nullable=False, default='')
    utm_id = sa.orm.mapped_column(
        sa.Unicode(250), nullable=False, default='', index=True
    )
    utm_campaign = sa.orm.mapped_column(
        sa.Unicode(250), nullable=False, default='', index=True
    )
    # Google click id (for AdWords)
    gclid = sa.orm.mapped_column(
        sa.Unicode(250), nullable=False, default='', index=True
    )


if TYPE_CHECKING:
    from .invoice import Invoice
    from .item_collection import ItemCollection
    from .payment import OnlinePayment, PaymentTransaction
    from .user import Organization, User
