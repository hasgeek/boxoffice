# -*- coding: utf-8 -*-

from collections import OrderedDict
from datetime import datetime
from coaster.utils import LabeledEnum, isoweek_datetime
from isoweek import Week
from baseframe import __
from boxoffice.models import db, BaseMixin, Order, ORDER_STATUS
from ..extapi import RAZORPAY_PAYMENT_STATUS

__all__ = ['OnlinePayment', 'PaymentTransaction', 'CURRENCY', 'CURRENCY_SYMBOL', 'TRANSACTION_TYPE']


class TRANSACTION_METHOD(LabeledEnum):
    ONLINE = (0, __("Online"))
    CASH = (1, __("Cash"))
    BANK_TRANSFER = (2, __("Bank Transfer"))


class TRANSACTION_TYPE(LabeledEnum):
    PAYMENT = (0, __("Payment"))
    REFUND = (1, __("Refund"))
    # CREDIT = (2, __("Credit"))


class OnlinePayment(BaseMixin, db.Model):
    """
    Represents payments made through a payment gateway.
    Supports Razorpay only.
    """
    __tablename__ = 'online_payment'
    __uuid_primary_key__ = True
    customer_order_id = db.Column(None, db.ForeignKey('customer_order.id'), nullable=False)
    order = db.relationship(Order, backref=db.backref('online_payments', cascade='all, delete-orphan'))

    # Payment id issued by the payment gateway
    pg_paymentid = db.Column(db.Unicode(80), nullable=False)
    # Payment status issued by the payment gateway
    pg_payment_status = db.Column(db.Integer, nullable=False)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    failed_at = db.Column(db.DateTime, nullable=True)

    def confirm(self):
        """Confirms a payment, sets confirmed_at and pg_payment_status."""
        self.confirmed_at = datetime.utcnow()
        self.pg_payment_status = RAZORPAY_PAYMENT_STATUS.CAPTURED

    def fail(self):
        """Fails a payment, sets failed_at."""
        self.pg_payment_status = RAZORPAY_PAYMENT_STATUS.FAILED
        self.failed_at = datetime.utcnow()


class PaymentTransaction(BaseMixin, db.Model):
    """
    Models transactions made with a customer.
    A transaction can either be of type 'Payment', 'Refund', 'Credit',
    """
    __tablename__ = 'payment_transaction'
    __uuid_primary_key__ = True

    customer_order_id = db.Column(None, db.ForeignKey('customer_order.id'), nullable=False)
    order = db.relationship(Order, backref=db.backref('transactions', cascade='all, delete-orphan', lazy="dynamic"))
    online_payment_id = db.Column(None, db.ForeignKey('online_payment.id'), nullable=True)
    online_payment = db.relationship(OnlinePayment, backref=db.backref('transactions', cascade='all, delete-orphan'))
    amount = db.Column(db.Numeric, nullable=False)
    currency = db.Column(db.Unicode(3), nullable=False)
    transaction_type = db.Column(db.Integer, default=TRANSACTION_TYPE.PAYMENT, nullable=False)
    transaction_method = db.Column(db.Integer, default=TRANSACTION_METHOD.ONLINE, nullable=False)
    # Eg: reference number for a bank transfer
    transaction_ref = db.Column(db.Unicode(80), nullable=True)
    refunded_at = db.Column(db.DateTime, nullable=True)
    internal_note = db.Column(db.Text, nullable=True)
    note_to_user = db.Column(db.Text, nullable=True)


def get_refund_transactions(self):
    return self.transactions.filter_by(transaction_type=TRANSACTION_TYPE.REFUND)

Order.get_refund_transactions = get_refund_transactions


def get_payment_transactions(self):
    return self.transactions.filter_by(transaction_type=TRANSACTION_TYPE.PAYMENT)

Order.get_payment_transactions = get_payment_transactions


def order_paid_amount(self):
    return sum([order_transaction.amount for order_transaction in self.get_payment_transactions()])

Order.paid_amount = property(order_paid_amount)


def order_refunded_amount(self):
    return sum([order_transaction.amount for order_transaction in self.get_refund_transactions()])

Order.refunded_amount = property(order_refunded_amount)


def order_net_amount(self):
    return self.paid_amount - self.refunded_amount

Order.net_amount = property(order_net_amount)


class CURRENCY(LabeledEnum):
    INR = (u"INR", __("INR"))


class CURRENCY_SYMBOL(LabeledEnum):
    INR = (u'INR', u'₹')


def calculate_weekly_refunds(item_collection_ids, user_tz, year):
    """
    Calculates refunds per week for a given set of item_collection_ids in a given year,
    in the user's timezone.
    """
    ordered_week_refunds = OrderedDict()
    for year_week in Week.weeks_of_year(year):
        ordered_week_refunds[year_week.week] = 0
    start_at = isoweek_datetime(year, 1, user_tz)
    end_at = isoweek_datetime(year + 1, 1, user_tz)

    week_refunds = db.session.query('sales_week', 'sum').from_statement(db.text('''
        SELECT EXTRACT(WEEK FROM payment_transaction.created_at AT TIME ZONE 'UTC' AT TIME ZONE :timezone)
        AS sales_week, SUM(payment_transaction.amount) AS sum
        FROM customer_order INNER JOIN payment_transaction on payment_transaction.customer_order_id = customer_order.id
        WHERE customer_order.status IN :statuses AND customer_order.item_collection_id IN :item_collection_ids
        AND payment_transaction.transaction_type = :transaction_type
        AND payment_transaction.created_at AT TIME ZONE 'UTC' AT TIME ZONE :timezone
            >= :start_at
        AND payment_transaction.created_at AT TIME ZONE 'UTC' AT TIME ZONE :timezone
            < :end_at
        GROUP BY sales_week ORDER BY sales_week;
        ''')).params(timezone=user_tz, statuses=tuple(ORDER_STATUS.TRANSACTION), transaction_type=TRANSACTION_TYPE.REFUND,
        start_at=start_at, end_at=end_at, item_collection_ids=tuple(item_collection_ids)).all()

    for week_refund in week_refunds:
        ordered_week_refunds[int(week_refund.sales_week)] = week_refund.sum

    return ordered_week_refunds
