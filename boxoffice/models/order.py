import random
from datetime import datetime
import decimal
from collections import namedtuple
from boxoffice.models import db, BaseMixin, User, Item, ItemCollection
from coaster.utils import LabeledEnum, buid
from baseframe import __

__all__ = ['Order', 'LineItem', 'PaymentTransaction']


class ORDER_STATUS(LabeledEnum):
    PURCHASE_ORDER = (0, __("Purchase Order"))
    SALES_ORDER = (1, __("Sales Order"))
    INVOICE = (2, __("Invoice"))
    CANCELLED = (3, __("Cancelled Order"))


class Order(BaseMixin, db.Model):
    __tablename__ = 'customer_order'
    __uuid_primary_key__ = True
    __tableargs__ = (db.UniqueConstraint('item_collection_id', 'order_hash'),
                     db.UniqueConstraint('access_token'))

    user_id = db.Column(None, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship(User,
                           backref=db.backref('orders',
                                              cascade='all, delete-orphan'))
    item_collection_id = db.Column(None,
                                   db.ForeignKey('item_collection.id'),
                                   nullable=False)
    item_collection = db.relationship(ItemCollection,
                                      backref=db.backref('orders', cascade='all, delete-orphan'))  # noqa
    status = db.Column(db.Integer,
                       default=ORDER_STATUS.PURCHASE_ORDER, nullable=False)

    initiated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    invoiced_at = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)

    access_token = db.Column(db.Unicode(22), nullable=False, default=buid)

    buyer_email = db.Column(db.Unicode(254), nullable=False)
    buyer_fullname = db.Column(db.Unicode(80), nullable=False)
    buyer_phone = db.Column(db.Unicode(13), nullable=False)

    order_hash = db.Column(db.Unicode(120), nullable=True)

    def invoice(self):
        """Sets invoiced_at, status and order_hash"""
        self.invoiced_at = datetime.utcnow()
        self.status = ORDER_STATUS.INVOICE
        self.order_hash = unicode(random.randrange(1, 9999999999))

    def get_amounts(self):
        """
        Calculates and returns the order's base_amount,
        discounted_amount and final_amount
        as a namedtuple
        """
        base_amount = (decimal.Decimal(0))
        discounted_amount = (decimal.Decimal(0))
        final_amount = (decimal.Decimal(0))
        for line_item in self.line_items:
            base_amount += line_item.base_amount
            discounted_amount += line_item.discounted_amount
            final_amount += line_item.final_amount
        order_amounts = namedtuple('OrderAmounts',
                                   ['base_amount',
                                    'discounted_amount',
                                    'final_amount'])
        return order_amounts(base_amount, discounted_amount, final_amount)


class LINE_ITEM_STATUS(LabeledEnum):
    CONFIRMED = (0, __("Confirmed"))
    CANCELLED = (1, __("Cancelled"))


class LineItem(BaseMixin, db.Model):
    __tablename__ = 'line_item'
    __uuid_primary_key__ = True
    customer_order_id = db.Column(None,
                                  db.ForeignKey('customer_order.id'),
                                  nullable=False)
    order = db.relationship(Order,
                            backref=db.backref('line_items',
                                               cascade='all, delete-orphan',
                                               lazy="dynamic"))

    item_id = db.Column(None, db.ForeignKey('item.id'), nullable=False)
    item = db.relationship(Item,
                           backref=db.backref('line_items',
                                              cascade='all, delete-orphan'))

    quantity = db.Column(db.Integer, nullable=False)
    base_amount = db.Column(db.Numeric,
                            default=decimal.Decimal(0), nullable=False)
    discounted_amount = db.Column(db.Numeric,
                                  default=decimal.Decimal(0), nullable=False)
    final_amount = db.Column(db.Numeric,
                             default=decimal.Decimal(0), nullable=False)
    status = db.Column(db.Integer,
                       default=LINE_ITEM_STATUS.CONFIRMED, nullable=False)
    ordered_at = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    # tax_amount = db.Column(db.Numeric, default=0.0, nullable=False)

    @classmethod
    def populate_amounts_and_discounts(cls, price, quantity, discount_policies):
        """
        Returns a tuple consisting of a named tuple with
        the line item's amounts, and an array
        of the applied discount policies

        # TODO: What if the price changes by
        the time the computation below happens?
        """
        amounts = namedtuple('Amounts',
                             ['base_amount',
                              'discounted_amount', 'final_amount'])
        base_amount = price * quantity
        discounted_amount = decimal.Decimal(0)

        discount_policy_dicts = []
        for discount_policy in discount_policies:
            discount_policy_dict = {
                'id': discount_policy.id,
                'activated': False,
                'title': discount_policy.title
            }
            if discount_policy.is_valid(quantity):
                discounted_amount += (discount_policy.percentage * base_amount)/decimal.Decimal(100.0)  # noqa
                discount_policy_dict['activated'] = True
            discount_policy_dicts.append(discount_policy_dict)

        return (amounts(base_amount, discounted_amount,
                        base_amount - discounted_amount),
                discount_policy_dicts)

    def cancel(self):
        """
        Sets status and cancelled_at. To update the quantity
        create, a new line item with the required quantity
        """
        self.status = LINE_ITEM_STATUS.CANCELLED
        self.cancelled_at = datetime.utcnow()
        db.session.add(self)

    @classmethod
    def confirmed(cls, order):
        return cls.query.filter_by(order=order,
                                   status=LINE_ITEM_STATUS.CONFIRMED).all()

    @classmethod
    def cancelled(cls, order):
        return cls.query.filter_by(order=order,
                                   status=LINE_ITEM_STATUS.CANCELLED).all()


class PAYMENT_TYPES(LabeledEnum):
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


class Payment(BaseMixin, db.Model):
    """
    Represents online payments made through Razorpay.
    """
    __tablename__ = 'payment'
    __uuid_primary_key__ = True
    customer_order_id = db.Column(None,
                                  db.ForeignKey('customer_order.id'),
                                  nullable=False)
    order = db.relationship(Order,
                            backref=db.backref('payments',
                                               cascade='all, delete-orphan',
                                               lazy="dynamic"))

    # Payment id issued by the payment gateway
    pg_payment_id = db.Column(db.Unicode(80), nullable=False)
    status = db.Column(db.Integer,
                       default=PAYMENT_TYPES.CREATED, nullable=False)
    captured_at = db.Column(db.DateTime, nullable=True)
    failed_at = db.Column(db.DateTime, nullable=True)

    def is_captured(self):
        return self.status == PAYMENT_TYPES.CAPTURED

    def capture(self):
        self.status = PAYMENT_TYPES.CAPTURED
        self.captured_at = datetime.utcnow()

    def fail(self):
        self.status = PAYMENT_TYPES.FAILED
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
    This model records transactions made with a customer.
    A transaction can either be of type 'Payment', 'Refund', 'Credit',
    """
    __tablename__ = 'payment_transaction'
    __uuid_primary_key__ = True

    customer_order_id = db.Column(None,
                                  db.ForeignKey('customer_order.id'),
                                  nullable=False)
    order = db.relationship(Order,
                            backref=db.backref('transactions',
                                               cascade='all, delete-orphan',
                                               lazy="dynamic"))
    payment_id = db.Column(None, db.ForeignKey('payment.id'), nullable=True)
    payment = db.relationship(Payment,
                              backref=db.backref('transactions',
                                                 cascade='all, delete-orphan'))
    amount = db.Column(db.Numeric, default=decimal.Decimal(0), nullable=False)
    currency = db.Column(db.Unicode(3), nullable=False, default=u'INR')
    transaction_type = db.Column(db.Integer,
                                 default=TRANSACTION_TYPES.PAYMENT,
                                 nullable=False)
    transaction_method = db.Column(db.Integer,
                                   default=TRANSACTION_METHODS.ONLINE,
                                   nullable=False)
