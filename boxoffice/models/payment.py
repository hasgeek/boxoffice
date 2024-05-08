from __future__ import annotations

from collections import OrderedDict
from collections.abc import Iterable
from datetime import tzinfo
from decimal import Decimal
from uuid import UUID

from isoweek import Week
from sqlalchemy.sql import func

from coaster.utils import isoweek_datetime

from . import (
    BaseMixin,
    Mapped,
    MarkdownColumn,
    Model,
    db,
    relationship,
    sa,
    timestamptz,
)
from .enums import (
    OrderStatus,
    RazorpayPaymentStatus,
    TransactionMethodEnum,
    TransactionTypeEnum,
)
from .user import User

__all__ = ['OnlinePayment', 'PaymentTransaction']


class OnlinePayment(BaseMixin[UUID, User], Model):
    """Represents payments made through a payment gateway. Supports Razorpay only."""

    __tablename__ = 'online_payment'
    customer_order_id: Mapped[UUID] = sa.orm.mapped_column(
        sa.ForeignKey('customer_order.id')
    )
    order: Mapped[Order] = relationship(back_populates='online_payments')

    # Payment id issued by the payment gateway
    pg_paymentid: Mapped[str] = sa.orm.mapped_column(sa.Unicode(80), unique=True)
    # Payment status issued by the payment gateway
    pg_payment_status: Mapped[int]
    confirmed_at: Mapped[timestamptz | None]
    failed_at: Mapped[timestamptz | None]
    transactions: Mapped[list[PaymentTransaction]] = relationship(
        cascade='all, delete-orphan', back_populates='online_payment'
    )

    def confirm(self) -> None:
        """Confirm a payment, sets confirmed_at and pg_payment_status."""
        self.confirmed_at = func.utcnow()
        self.pg_payment_status = RazorpayPaymentStatus.CAPTURED

    def fail(self) -> None:
        """Fails a payment, sets failed_at."""
        self.pg_payment_status = RazorpayPaymentStatus.FAILED
        self.failed_at = func.utcnow()


class PaymentTransaction(BaseMixin[UUID, User], Model):
    """
    Models transactions made by a customer.

    A transaction can be one of type 'Payment', 'Refund', 'Credit'.
    """

    __tablename__ = 'payment_transaction'

    customer_order_id: Mapped[UUID] = sa.orm.mapped_column(
        sa.ForeignKey('customer_order.id')
    )
    order: Mapped[Order] = relationship(back_populates='transactions')
    online_payment_id: Mapped[UUID | None] = sa.orm.mapped_column(
        sa.ForeignKey('online_payment.id')
    )
    online_payment: Mapped[OnlinePayment | None] = relationship(
        back_populates='transactions'
    )
    amount: Mapped[Decimal]
    currency: Mapped[str] = sa.orm.mapped_column(sa.Unicode(3))
    transaction_type: Mapped[int] = sa.orm.mapped_column(
        default=TransactionTypeEnum.PAYMENT
    )
    transaction_method: Mapped[int] = sa.orm.mapped_column(
        default=TransactionMethodEnum.ONLINE
    )
    # Eg: reference number for a bank transfer
    transaction_ref: Mapped[str | None] = sa.orm.mapped_column(sa.Unicode(80))
    refunded_at: Mapped[timestamptz | None]
    internal_note: Mapped[str | None] = sa.orm.mapped_column(sa.Unicode(250))
    refund_description: Mapped[str | None] = sa.orm.mapped_column(sa.Unicode(250))
    note_to_user = MarkdownColumn('note_to_user', nullable=True)
    # Refund id issued by the payment gateway
    pg_refundid: Mapped[str | None] = sa.orm.mapped_column(sa.Unicode(80), unique=True)


def calculate_weekly_refunds(
    menu_ids: Iterable[UUID], user_tz: str | tzinfo, year: int
) -> OrderedDict[int, int]:
    """Calculate refunds per week of the year for given menu_ids."""
    ordered_week_refunds = OrderedDict()
    for year_week in Week.weeks_of_year(year):
        ordered_week_refunds[year_week.week] = 0
    start_at = isoweek_datetime(year, 1, user_tz)
    end_at = isoweek_datetime(year + 1, 1, user_tz)

    week_refunds = db.session.execute(
        sa.select(
            sa.func.extract(
                'WEEK',
                sa.func.timezone(
                    user_tz, sa.func.timezone('UTC', PaymentTransaction.created_at)
                ),
            ).label('sales_week'),
            sa.func.sum(PaymentTransaction.amount).label('sum'),
        )
        .select_from(PaymentTransaction, Order)
        .where(
            PaymentTransaction.customer_order_id == Order.id,
            Order.status.in_(
                [
                    OrderStatus.SALES_ORDER.value,
                    OrderStatus.INVOICE.value,
                    OrderStatus.CANCELLED.value,
                ]
            ),
            Order.menu_id.in_(menu_ids),
            PaymentTransaction.transaction_type == TransactionTypeEnum.REFUND,
            sa.func.timezone(
                user_tz, sa.func.timezone('UTC', PaymentTransaction.created_at)
            )
            >= start_at,
            sa.func.timezone(
                user_tz, sa.func.timezone('UTC', PaymentTransaction.created_at)
            )
            < end_at,
        )
        .group_by('sales_week')
        .order_by('sales_week')
    ).all()

    for week_refund in week_refunds:
        ordered_week_refunds[int(week_refund.sales_week)] = week_refund.sum

    return ordered_week_refunds


# Tail imports
from .order import Order
