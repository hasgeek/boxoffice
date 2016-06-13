# -*- coding: utf-8 -*-

from datetime import datetime
from coaster.utils import LabeledEnum
from baseframe import __
from boxoffice.models import db, BaseMixin, Order
from ..extapi import RAZORPAY_PAYMENT_STATUS

__all__ = ['OnlinePayment', 'PaymentTransaction', 'CURRENCY']


class TRANSACTION_METHOD(LabeledEnum):
    ONLINE = (0, __("Online"))
    CASH = (1, __("Cash"))


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
        """
        Confirms a payment, sets confirmed_at and pg_payment_status.
        """
        self.confirmed_at = datetime.utcnow()
        self.pg_payment_status = RAZORPAY_PAYMENT_STATUS.CAPTURED

    def fail(self):
        """
        Fails a payment, sets failed_at.
        """
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


class CURRENCY(LabeledEnum):
    INR = (u"INR", __("INR"))
