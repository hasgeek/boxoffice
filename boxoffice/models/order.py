import random
from datetime import datetime
import decimal
from collections import namedtuple
from boxoffice.models import db, BaseMixin, User, Item, ItemCollection, Price
from coaster.utils import LabeledEnum, buid
from baseframe import __

__all__ = ['Order', 'LineItem', 'OnlinePayment', 'PaymentTransaction', 'ORDER_STATUS']


class ORDER_STATUS(LabeledEnum):
    PURCHASE_ORDER = (0, __("Purchase Order"))
    SALES_ORDER = (1, __("Sales Order"))
    INVOICE = (2, __("Invoice"))
    CANCELLED = (3, __("Cancelled Order"))


def gen_order_hash():
    return unicode(random.randrange(1, 9999999999))


class Order(BaseMixin, db.Model):
    __tablename__ = 'customer_order'
    __uuid_primary_key__ = True
    __tableargs__ = (db.UniqueConstraint('item_collection_id', 'order_hash'),
        db.UniqueConstraint('access_token'))

    user_id = db.Column(None, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship(User, backref=db.backref('orders', cascade='all, delete-orphan'))
    item_collection_id = db.Column(None, db.ForeignKey('item_collection.id'), nullable=False)
    item_collection = db.relationship(ItemCollection, backref=db.backref('orders', cascade='all, delete-orphan', lazy="dynamic"))  # noqa
    status = db.Column(db.Integer, default=ORDER_STATUS.PURCHASE_ORDER, nullable=False)

    initiated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime, nullable=True)
    invoiced_at = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)

    access_token = db.Column(db.Unicode(22), nullable=False, default=buid)

    buyer_email = db.Column(db.Unicode(254), nullable=False)
    buyer_fullname = db.Column(db.Unicode(80), nullable=False)
    buyer_phone = db.Column(db.Unicode(16), nullable=False)

    order_hash = db.Column(db.Unicode(120), nullable=True, default=gen_order_hash)

    def confirm_sale(self):
        """
        Updates the status to Sales Order
        """
        self.status = ORDER_STATUS.SALES_ORDER
        self.paid_at = datetime.utcnow()

    def invoice(self):
        """Sets invoiced_at, status and order_hash"""
        self.invoiced_at = datetime.utcnow()
        self.status = ORDER_STATUS.INVOICE

    def get_amounts(self):
        """
        Calculates and returns the order's base_amount, discounted_amount and
        final_amount as a namedtuple
        """
        base_amount = (decimal.Decimal(0))
        discounted_amount = (decimal.Decimal(0))
        final_amount = (decimal.Decimal(0))
        for line_item in self.line_items:
            base_amount += line_item.base_amount
            discounted_amount += line_item.discounted_amount
            final_amount += line_item.final_amount
        order_amounts = namedtuple('OrderAmounts', ['base_amount', 'discounted_amount', 'final_amount'])
        return order_amounts(base_amount, discounted_amount, final_amount)

    def cancel(self):
        """
        Cancels the order and all the associated line items.
        """
        for line_item in LineItem.get_confirmed(self):
            line_item.cancel()
        self.status = ORDER_STATUS.CANCELLED
        self.cancelled_at = datetime.utcnow()

    def make_line_items(self, line_item_dicts):
        """
        Accepts a list of dictionaries in the format {'item_id': 'x', 'quantity': y}
        Makes line item objects for the order.
        """
        for line_item_dict in line_item_dicts:
            item = Item.query.get(line_item_dict.get('item_id'))
            line_item = LineItem(item=item, order=self, ordered_at=datetime.utcnow())

            line_item.base_amount = Price.current(item).amount
            discounted_amount = decimal.Decimal(0)
            for discount_policy in item.discount_policies:
                if discount_policy.is_valid(len(item.line_items)):
                    discounted_amount += (discount_policy.percentage * line_item.base_amount)/decimal.Decimal(100.0)  # noqa

            line_item.discounted_amount = discounted_amount
            line_item.final_amount = line_item.base_amount - line_item.discounted_amount
            line_item.discount_policies.append(discount_policy)

        return self


class LINE_ITEM_STATUS(LabeledEnum):
    CONFIRMED = (0, __("Confirmed"))
    CANCELLED = (1, __("Cancelled"))


line_item_payment_transaction = db.Table('line_item_payment_transaction', db.Model.metadata,
    db.Column('line_item_id', None, db.ForeignKey('line_item.id'), primary_key=True),
    db.Column('payment_transaction_id', None, db.ForeignKey('payment_transaction.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow, nullable=False))


line_item_discount_policy = db.Table('line_item_discount_policy', db.Model.metadata,
    db.Column('line_item_id', None, db.ForeignKey('line_item.id'), primary_key=True),
    db.Column('discount_policy_id', None, db.ForeignKey('discount_policy.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow, nullable=False))


class LineItem(BaseMixin, db.Model):
    """
    Line Items MUST NOT be modified OR deleted, they must only be created or cancelled.
    As an example, if a user requests the quantity to be changed from x to y, following is
    the workflow to manage such a transaction:
        1. Cancel the original line item.
        2. Create a new line item with the requested 'y' quantity.
        3. Compute the order total, and issue a refund if required.
    """
    __tablename__ = 'line_item'
    __uuid_primary_key__ = True
    customer_order_id = db.Column(None, db.ForeignKey('customer_order.id'), nullable=False)
    order = db.relationship(Order, backref=db.backref('line_items', cascade='all, delete-orphan'))

    item_id = db.Column(None, db.ForeignKey('item.id'), nullable=False)
    item = db.relationship(Item, backref=db.backref('line_items', cascade='all, delete-orphan'))

    base_amount = db.Column(db.Numeric, default=decimal.Decimal(0), nullable=False)
    discounted_amount = db.Column(db.Numeric, default=decimal.Decimal(0), nullable=False)
    final_amount = db.Column(db.Numeric, default=decimal.Decimal(0), nullable=False)
    status = db.Column(db.Integer, default=LINE_ITEM_STATUS.CONFIRMED, nullable=False)
    ordered_at = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    cancellable = db.Column(db.Boolean, nullable=False, default=True)
    transferrable = db.Column(db.Boolean, nullable=True, default=True)
    assignee_email = db.Column(db.Unicode(254), nullable=False)
    assignee_fullname = db.Column(db.Unicode(80), nullable=False)
    assignee_phone = db.Column(db.Unicode(16), nullable=False)

    discount_policies = db.relationship('DiscountPolicy', secondary=line_item_discount_policy)
    payment_transactions = db.relationship('PaymentTransaction', secondary=line_item_payment_transaction)
    # tax_amount = db.Column(db.Numeric, default=0.0, nullable=False)

    def cancel(self):
        """
        Sets status and cancelled_at. To update the quantity
        create, a new line item with the required quantity
        """
        self.status = LINE_ITEM_STATUS.CANCELLED
        self.cancelled_at = datetime.utcnow()

    @classmethod
    def get_confirmed(cls, order):
        """
        Returns an order's confirmed line items.
        """
        return cls.query.filter_by(order=order, status=LINE_ITEM_STATUS.CONFIRMED).all()

    @classmethod
    def get_cancelled(cls, order):
        """
        Returns an order's cancelled line items.
        """
        return cls.query.filter_by(order=order, status=LINE_ITEM_STATUS.CANCELLED).all()


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
    customer_order_id = db.Column(None,
                                  db.ForeignKey('customer_order.id'),
                                  nullable=False)
    order = db.relationship(Order,
                            backref=db.backref('online_payments',
                                               cascade='all, delete-orphan',
                                               lazy="dynamic"))

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
    # line_items = db.relationship('LineItem', secondary=line_item_payment_transaction)
