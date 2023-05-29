from __future__ import annotations

from collections import OrderedDict
from decimal import Decimal
from uuid import UUID

from sqlalchemy.sql import func

from isoweek import Week

from coaster.utils import isoweek_datetime

from . import BaseMixin, Mapped, MarkdownColumn, Model, backref, db, relationship, sa
from .enums import RAZORPAY_PAYMENT_STATUS, TRANSACTION_METHOD, TRANSACTION_TYPE
from .item_collection import ItemCollection
from .order import ORDER_STATUS, Order

__all__ = [
    'OnlinePayment',
    'PaymentTransaction',
]


class OnlinePayment(BaseMixin, Model):
    """Represents payments made through a payment gateway. Supports Razorpay only."""

    __tablename__ = 'online_payment'
    __uuid_primary_key__ = True
    customer_order_id: Mapped[UUID] = sa.orm.mapped_column(
        sa.ForeignKey('customer_order.id'), nullable=False
    )
    order = relationship(
        Order, backref=backref('online_payments', cascade='all, delete-orphan')
    )

    # Payment id issued by the payment gateway
    pg_paymentid = sa.orm.mapped_column(sa.Unicode(80), nullable=False, unique=True)
    # Payment status issued by the payment gateway
    pg_payment_status = sa.orm.mapped_column(sa.Integer, nullable=False)
    confirmed_at = sa.orm.mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    failed_at = sa.orm.mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)

    def confirm(self) -> None:
        """Confirm a payment, sets confirmed_at and pg_payment_status."""
        self.confirmed_at = func.utcnow()
        self.pg_payment_status = RAZORPAY_PAYMENT_STATUS.CAPTURED

    def fail(self) -> None:
        """Fails a payment, sets failed_at."""
        self.pg_payment_status = RAZORPAY_PAYMENT_STATUS.FAILED
        self.failed_at = func.utcnow()


class PaymentTransaction(BaseMixin, Model):
    """
    Models transactions made by a customer.

    A transaction can be one of type 'Payment', 'Refund', 'Credit'.
    """

    __tablename__ = 'payment_transaction'
    __uuid_primary_key__ = True

    customer_order_id: Mapped[UUID] = sa.orm.mapped_column(
        sa.ForeignKey('customer_order.id'), nullable=False
    )
    order = relationship(Order, back_populates='transactions')
    online_payment_id: Mapped[UUID] = sa.orm.mapped_column(
        sa.ForeignKey('online_payment.id'), nullable=True
    )
    online_payment = relationship(
        OnlinePayment,
        backref=backref('transactions', cascade='all, delete-orphan'),
    )
    amount = sa.orm.mapped_column(sa.Numeric, nullable=False)
    currency = sa.orm.mapped_column(sa.Unicode(3), nullable=False)
    transaction_type = sa.orm.mapped_column(
        sa.Integer, default=TRANSACTION_TYPE.PAYMENT, nullable=False
    )
    transaction_method = sa.orm.mapped_column(
        sa.Integer, default=TRANSACTION_METHOD.ONLINE, nullable=False
    )
    # Eg: reference number for a bank transfer
    transaction_ref = sa.orm.mapped_column(sa.Unicode(80), nullable=True)
    refunded_at = sa.orm.mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    internal_note = sa.orm.mapped_column(sa.Unicode(250), nullable=True)
    refund_description = sa.orm.mapped_column(sa.Unicode(250), nullable=True)
    note_to_user = MarkdownColumn('note_to_user', nullable=True)
    # Refund id issued by the payment gateway
    pg_refundid = sa.orm.mapped_column(sa.Unicode(80), nullable=True, unique=True)


def item_collection_net_sales(self):
    """Return the net revenue for an item collection."""
    total_paid = (
        db.session.query(sa.column('sum'))
        .from_statement(
            sa.text(
                '''
                SELECT SUM(amount) FROM payment_transaction
                INNER JOIN customer_order
                    ON payment_transaction.customer_order_id = customer_order.id
                WHERE transaction_type=:transaction_type
                    AND customer_order.item_collection_id = :item_collection_id
                '''
            )
        )
        .params(transaction_type=TRANSACTION_TYPE.PAYMENT, item_collection_id=self.id)
        .scalar()
    )

    total_refunded = (
        db.session.query(sa.column('sum'))
        .from_statement(
            sa.text(
                '''
                SELECT SUM(amount) FROM payment_transaction
                INNER JOIN customer_order
                    ON payment_transaction.customer_order_id = customer_order.id
                WHERE transaction_type=:transaction_type
                    AND customer_order.item_collection_id = :item_collection_id
                '''
            )
        )
        .params(transaction_type=TRANSACTION_TYPE.REFUND, item_collection_id=self.id)
        .scalar()
    )

    if total_paid and total_refunded:
        return total_paid - total_refunded
    if total_paid:
        return total_paid
    return Decimal('0')


ItemCollection.net_sales = property(item_collection_net_sales)


def calculate_weekly_refunds(item_collection_ids, user_tz, year):
    """Calculate refunds per week of the year for given item_collection_ids."""
    ordered_week_refunds = OrderedDict()
    for year_week in Week.weeks_of_year(year):
        ordered_week_refunds[year_week.week] = 0
    start_at = isoweek_datetime(year, 1, user_tz)
    end_at = isoweek_datetime(year + 1, 1, user_tz)

    week_refunds = (
        db.session.query(sa.column('sales_week'), sa.column('sum'))
        .from_statement(
            sa.text(
                '''
                SELECT
                    EXTRACT(
                        WEEK FROM payment_transaction.created_at
                        AT TIME ZONE 'UTC' AT TIME ZONE :timezone
                        ) AS sales_week,
                    SUM(payment_transaction.amount) AS sum
                FROM customer_order
                INNER JOIN payment_transaction
                    ON payment_transaction.customer_order_id = customer_order.id
                WHERE customer_order.status IN :statuses
                    AND customer_order.item_collection_id IN :item_collection_ids
                    AND payment_transaction.transaction_type = :transaction_type
                    AND payment_transaction.created_at
                        AT TIME ZONE 'UTC' AT TIME ZONE :timezone >= :start_at
                    AND payment_transaction.created_at
                        AT TIME ZONE 'UTC' AT TIME ZONE :timezone < :end_at
                GROUP BY sales_week ORDER BY sales_week;
                '''
            )
        )
        .params(
            timezone=user_tz,
            statuses=tuple(ORDER_STATUS.TRANSACTION),
            transaction_type=TRANSACTION_TYPE.REFUND,
            start_at=start_at,
            end_at=end_at,
            item_collection_ids=tuple(item_collection_ids),
        )
        .all()
    )

    for week_refund in week_refunds:
        ordered_week_refunds[int(week_refund.sales_week)] = week_refund.sum

    return ordered_week_refunds
