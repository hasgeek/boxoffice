from datetime import datetime
import decimal
from coaster.utils import LabeledEnum
from baseframe import __
from boxoffice.models import db, BaseMixin, Order

__all__ = ['OnlinePayment', 'PaymentTransaction']


class RAZORPAY_PAYMENT_STATUS(LabeledEnum):
    """
    Reflects payment statuses as specified in
    https://docs.razorpay.com/docs/return-objects
    """
    CREATED = (0, __("Created"))
    AUTHORIZED = (1, __("Authorized"))
    CAPTURED = (2, __("Captured"))
    # Only fully refunded payments.
    REFUNDED = (3, __("Refunded"))
    FAILED = (4, __("Failed"))


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
    pg_payment_id = db.Column(db.Unicode(80), nullable=False)
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


class TRANSACTION_METHODS(LabeledEnum):
    ONLINE = (0, __("Online"))
    CASH = (1, __("Cash"))


class TRANSACTION_TYPES(LabeledEnum):
    PAYMENT = (0, __("Payment"))
    REFUND = (1, __("Refund"))
    # CREDIT = (2, __("Credit"))


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
    amount = db.Column(db.Numeric, default=decimal.Decimal(0), nullable=False)
    currency = db.Column(db.Unicode(3), nullable=False, default=u'INR')
    transaction_type = db.Column(db.Integer, default=TRANSACTION_TYPES.PAYMENT, nullable=False)
    transaction_method = db.Column(db.Integer, default=TRANSACTION_METHODS.ONLINE, nullable=False)
