import decimal
import requests
from boxoffice.models import db, BaseMixin, User, Item, Inventory, Price
from coaster.utils import LabeledEnum
from coaster.sqlalchemy import JsonDict
from baseframe import __

__all__ = ['Order', 'LineItem', 'Transaction']


class ORDER_STATUS(LabeledEnum):
    PURCHASE_ORDER = (0, __("Purchase Order"))
    SALES_ORDER = (1, __("Sales Order"))
    INVOICE = (2, __("Invoice"))
    CANCELLED = (3, __("Cancelled Order"))


class Order(BaseMixin, db.Model):
    __tablename__ = 'order'
    __uuid_primary_key__ = True
    user_id = db.Column(None, db.ForeignKey('user.id'))
    user = db.relationship(User, backref=db.backref('orders', cascade='all, delete-orphan'))
    inventory_id = db.Column(None, db.ForeignKey('inventory.id'), nullable=False)
    inventory = db.relationship(Inventory,
        backref=db.backref('orders', cascade='all, delete-orphan'))
    status = db.Column(db.Integer, default=ORDER_STATUS.PURCHASE_ORDER, nullable=False)
    base_amount = db.Column(db.Numeric, default=decimal.Decimal(0), nullable=False)
    discounted_amount = db.Column(db.Numeric, default=decimal.Decimal(0), nullable=False)
    final_amount = db.Column(db.Numeric, default=decimal.Decimal(0), nullable=False)

    def calculate(self, line_items):
        """
        - Creates line items given an array of line item dicts with item name and quantity
        - Calculates and sets the order's base_amount, discounted_amount and final_amount
        TODO: Calculate this whenever line item is touched
        """
        for line_item in line_items:
            item = Item.get(self.inventory, line_item.get('name'))
            line_item = LineItem(item=item, order=self, quantity=line_item.get('quantity'))
            line_item.calculate()

            self.base_amount = self.base_amount + line_item.base_amount
            self.discounted_amount = self.discounted_amount + line_item.discounted_amount
            self.final_amount = self.final_amount + line_item.final_amount


class LINE_ITEM_STATUS(LabeledEnum):
    CONFIRMED = (0, __("Confirmed"))
    CANCELLED = (1, __("Cancelled"))


class LineItem(BaseMixin, db.Model):
    __tablename__ = 'line_item'
    __uuid_primary_key__ = True
    order_id = db.Column(None, db.ForeignKey('order.id'))
    order = db.relationship(Order, backref=db.backref('line_items', cascade='all, delete-orphan', lazy="dynamic"))

    item_id = db.Column(None, db.ForeignKey('item.id'))
    item = db.relationship(Item, backref=db.backref('line_items', cascade='all, delete-orphan'))

    quantity = db.Column(db.Integer, nullable=False)
    base_amount = db.Column(db.Numeric, default=decimal.Decimal(0), nullable=False)
    discounted_amount = db.Column(db.Numeric, default=decimal.Decimal(0), nullable=False)
    final_amount = db.Column(db.Numeric, default=decimal.Decimal(0), nullable=False)
    status = db.Column(db.Integer, default=LINE_ITEM_STATUS.CONFIRMED, nullable=False)
    # tax_amount = db.Column(db.Numeric, default=0.0, nullable=False)


    def calculate(self):
        # TODO: What if the price changes by the time the computation below happens?
        self.base_amount = Price.current(self.item).amount * self.quantity
        for discount_policy in self.item.discount_policies:
            if self.quantity >= discount_policy.item_quantity_min and self.quantity <= discount_policy.item_quantity_max:
                self.discounted_amount = (discount_policy.percentage * self.base_amount)/decimal.Decimal(100.0)
        self.final_amount = self.base_amount - self.discounted_amount


    def cancel(self):
        """
        Sets the status to LINE_ITEM_STATUS.CANCELLED. To update the quantity
        create, a new line item with the required quantity
        """
        self.status = LINE_ITEM_STATUS.CANCELLED


    @classmethod
    def confirmed(cls, order):
        return cls.query.filter_by(order=order, status=LINE_ITEM_STATUS.CONFIRMED).all()

    @classmethod
    def cancelled(cls, order):
        return cls.query.filter_by(order=order, status=LINE_ITEM_STATUS.CANCELLED).all()


class PAYMENT_TYPES(LabeledEnum):
    """
    Reflects payment statuses as specified in https://docs.razorpay.com/docs/return-objects
    """
    CREATED = (0, __("Created"))
    AUTHORIZED = (1, __("Authorized"))
    CAPTURED = (2, __("Captured"))
    # Only fully refunded payments.
    REFUNDED = (3, __("Refunded"))
    FAILED = (4, __("Failed"))


class Payment(BaseMixin, db.Model):
    __tablename__ = 'payment'
    __uuid_primary_key__ = True
    order_id = db.Column(None, db.ForeignKey('order.id'))
    order = db.relationship(Order, backref=db.backref('payments', cascade='all, delete-orphan', lazy="dynamic"))

    # Payment id issued by the payment gateway
    pg_payment_id = db.Column(db.Unicode(80), nullable=False)
    status = db.Column(db.Integer, default=PAYMENT_TYPES.CREATED, nullable=False)

    def is_captured(self):
        return self.status == PAYMENT_TYPES.CAPTURED


    def capture(self):
        self.status = PAYMENT_TYPES.CAPTURED


    def fail(self):
        self.status = PAYMENT_TYPES.FAILED


class TRANSACTION_TYPES(LabeledEnum):
    PAYMENT = (0, __("Payment"))
    REFUND = (1, __("Refund"))
    # CREDIT = (2, __("Credit"))


class Transaction(BaseMixin, db.Model):
    """
    This model records transactions made with a customer.
    A transaction can either be of type 'Payment', 'Refund', 'Credit',
    """
    __tablename__ = 'transaction'
    __uuid_primary_key__ = True

    payment_id = db.Column(None, db.ForeignKey('payment.id'), nullable=False)
    payment = db.relationship(Payment, backref=db.backref('transactions', cascade='all, delete-orphan'))
    amount = db.Column(db.Numeric, default=decimal.Decimal(0), nullable=False)
    currency = db.Column(db.Unicode(3), nullable=False, default=u'INR')
    transaction_type = db.Column(db.Integer, default=TRANSACTION_TYPES.PAYMENT, nullable=False)
