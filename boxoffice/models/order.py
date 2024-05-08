from __future__ import annotations

import secrets
from dataclasses import dataclass
from decimal import Decimal
from functools import partial
from typing import TYPE_CHECKING, Any, NamedTuple
from uuid import UUID

from sqlalchemy.ext.orderinglist import ordering_list

from coaster.utils import utcnow

from . import (
    AppenderQuery,
    BaseMixin,
    DynamicMapped,
    Mapped,
    Model,
    relationship,
    sa,
    timestamptz,
    timestamptz_now,
)
from .enums import LineItemStatus, OrderStatus, TransactionTypeEnum
from .line_item import LineItem
from .user import Organization, User

__all__ = ['Order', 'OrderSession']


class OrderAmounts(NamedTuple):
    base_amount: Decimal
    discounted_amount: Decimal
    final_amount: Decimal
    confirmed_amount: Decimal


@dataclass
class LineItemGroup:
    # This dataclass uses Any types as the actual types are not imported yet
    ticket: Any
    count: int
    total_price: Decimal


def gen_receipt_no(organization: Organization) -> sa.ScalarSelect[int]:
    """Generate a sequential invoice number for an order, given an organization."""
    return (
        sa.select(sa.func.coalesce(sa.func.max(Order.receipt_no + 1), 1))
        .where(Order.organization_id == organization.id)
        .scalar_subquery()
    )


class Order(BaseMixin[UUID, User], Model):
    __tablename__ = 'customer_order'
    __table_args__ = (
        sa.UniqueConstraint('organization_id', 'invoice_no'),
        sa.UniqueConstraint('access_token'),
    )

    user_id: Mapped[int | None] = sa.orm.mapped_column(sa.ForeignKey('user.id'))
    user: Mapped[User | None] = relationship(back_populates='orders')
    menu_id: Mapped[UUID] = sa.orm.mapped_column(
        'item_collection_id', sa.ForeignKey('item_collection.id')
    )
    menu: Mapped[Menu] = relationship(back_populates='orders')
    organization_id: Mapped[int] = sa.orm.mapped_column(
        sa.ForeignKey('organization.id')
    )
    organization: Mapped[Organization] = relationship(back_populates='orders')
    status: Mapped[int] = sa.orm.mapped_column(default=OrderStatus.PURCHASE_ORDER)
    initiated_at: Mapped[timestamptz_now]
    paid_at: Mapped[timestamptz | None]
    invoiced_at: Mapped[timestamptz | None]
    cancelled_at: Mapped[timestamptz | None]
    access_token: Mapped[str] = sa.orm.mapped_column(
        sa.Unicode(22), default=partial(secrets.token_urlsafe, 16)
    )
    buyer_email: Mapped[str] = sa.orm.mapped_column(sa.Unicode(254))
    buyer_fullname: Mapped[str] = sa.orm.mapped_column(sa.Unicode(80))
    buyer_phone: Mapped[str] = sa.orm.mapped_column(sa.Unicode(16))

    # TODO: Rename column
    receipt_no: Mapped[int | None] = sa.orm.mapped_column('invoice_no')

    line_items: Mapped[list[LineItem]] = relationship(
        cascade='all, delete-orphan',
        order_by='LineItem.line_item_seq',
        collection_class=ordering_list('line_item_seq', count_from=1),
        back_populates='order',
    )
    session: Mapped[OrderSession] = relationship(
        cascade='all, delete-orphan', uselist=False, back_populates='order'
    )
    online_payments: Mapped[list[OnlinePayment]] = relationship(
        cascade='all, delete-orphan'
    )
    transactions: DynamicMapped[PaymentTransaction] = relationship(
        cascade='all, delete-orphan', lazy='dynamic', back_populates='order'
    )
    invoices: Mapped[list[Invoice]] = relationship(
        cascade='all, delete-orphan', back_populates='order'
    )

    confirmed_line_items: DynamicMapped[LineItem] = relationship(
        lazy='dynamic',
        primaryjoin=lambda: sa.and_(
            LineItem.customer_order_id == Order.id,
            LineItem.status == LineItemStatus.CONFIRMED,
        ),
        viewonly=True,
    )

    confirmed_and_cancelled_line_items: DynamicMapped[LineItem] = relationship(
        lazy='dynamic',
        primaryjoin=lambda: sa.and_(
            LineItem.customer_order_id == Order.id,
            LineItem.status.in_(
                [LineItemStatus.CONFIRMED.value, LineItemStatus.CANCELLED.value]
            ),
        ),
        viewonly=True,
    )

    initial_line_items: DynamicMapped[LineItem] = relationship(
        lazy='dynamic',
        primaryjoin=lambda: sa.and_(
            LineItem.customer_order_id == Order.id,
            LineItem.previous_id.is_(None),
            LineItem.status.in_(
                [
                    LineItemStatus.CONFIRMED.value,
                    LineItemStatus.VOID.value,
                    LineItemStatus.CANCELLED.value,
                ]
            ),
        ),
        viewonly=True,
    )

    def permissions(self, actor: User, inherited: set[str] | None = None) -> set:
        perms = super().permissions(actor, inherited)
        if self.organization.userid in actor.organizations_owned_ids():
            perms.add('org_admin')
        return perms

    def confirm_sale(self) -> None:
        """Update the status to OrderStatus.SALES_ORDER."""
        for line_item in self.line_items:
            line_item.confirm()
        self.receipt_no = gen_receipt_no(self.organization)
        self.status = OrderStatus.SALES_ORDER
        self.paid_at = utcnow()

    def invoice(self) -> None:
        """Set invoiced_at and status."""
        for line_item in self.line_items:
            line_item.confirm()
        self.invoiced_at = utcnow()
        self.status = OrderStatus.INVOICE

    def get_amounts(self, line_item_status: LineItemStatus) -> OrderAmounts:
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
        return self.status in [
            OrderStatus.SALES_ORDER.value,
            OrderStatus.INVOICE.value,
        ]

    def is_fully_assigned(self) -> bool:
        """Check if all the line items in an order have an assignee."""
        return all(
            line_item.current_assignee is not None
            for line_item in self.confirmed_line_items
        )

    @property
    def refund_transactions(self) -> AppenderQuery[PaymentTransaction]:
        return self.transactions.filter_by(transaction_type=TransactionTypeEnum.REFUND)

    @property
    def payment_transactions(self) -> AppenderQuery[PaymentTransaction]:
        return self.transactions.filter_by(transaction_type=TransactionTypeEnum.PAYMENT)

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


class OrderSession(BaseMixin[UUID, User], Model):
    """Records the referrer and utm headers for an order."""

    __tablename__ = 'order_session'

    customer_order_id: Mapped[UUID] = sa.orm.mapped_column(
        sa.ForeignKey('customer_order.id'), index=True, unique=False
    )
    order: Mapped[Order] = relationship(back_populates='session')

    referrer: Mapped[str | None] = sa.orm.mapped_column(sa.Unicode(2083))
    host: Mapped[str | None] = sa.orm.mapped_column(sa.UnicodeText)

    # Google Analytics parameters
    utm_source: Mapped[str] = sa.orm.mapped_column(
        sa.Unicode(250), default='', index=True
    )
    utm_medium: Mapped[str] = sa.orm.mapped_column(
        sa.Unicode(250), default='', index=True
    )
    utm_term: Mapped[str] = sa.orm.mapped_column(sa.Unicode(250), default='')
    utm_content: Mapped[str] = sa.orm.mapped_column(sa.Unicode(250), default='')
    utm_id: Mapped[str] = sa.orm.mapped_column(sa.Unicode(250), default='', index=True)
    utm_campaign: Mapped[str] = sa.orm.mapped_column(
        sa.Unicode(250), default='', index=True
    )
    # Google click id (for AdWords)
    gclid: Mapped[str] = sa.orm.mapped_column(sa.Unicode(250), default='', index=True)


if TYPE_CHECKING:
    from .invoice import Invoice
    from .menu import Menu
    from .payment import OnlinePayment, PaymentTransaction
