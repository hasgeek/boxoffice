from boxoffice.models import db, BaseNameMixin, User, IdMixin, Item
from coaster.utils import LabeledEnum
from coaster.sqlalchemy import JsonDict
from baseframe import __

__all__ = ['Order', 'LineItem', 'PaymentGateway', 'Payment']


class ORDER_STATUSES(LabeledEnum):
    PURCHASE_ORDER = (0, __("Purchase Order"))
    SALES_ORDER = (1, __("Sales Order"))
    INVOICE = (2, __("Invoice"))
    CANCELLED = (3, __("Cancelled Order"))


class Order(BaseNameMixin, db.Model):
    __tablename__ = 'order'
    __uuid_primary_key__ = True

    user_id = db.Column(None, db.ForeignKey('user.id'))
    user = db.relationship(User, backref=db.backref('orders', cascade='all, delete-orphan'))
    status = db.Column(db.Integer, default=ORDER_STATUSES.PURCHASE_ORDER, nullable=False)

    def __repr__(self):
        return u'<Order "{order}">'.format(order=self.id)

    # def cancel(self):
    #     # process refund
    #     for line_item in order.line_items:

    #     # if order.transactions.count():
    #     #     for transaction in order.transactions:
    #             # calculate refund amount
    #             # refund_amount = LineItem.refund_amount(transaction.amount)
    #             # Transaction(amount=)
    #     self.status = ORDER_STATUSES.CANCELLED


class LineItem(IdMixin, db.Model):
    __tablename__ = 'line_item'
    __uuid_primary_key__ = True

    order_id = db.Column(None, db.ForeignKey('order.id'))
    order = db.relationship(Order, backref=db.backref('line_items', cascade='all, delete-orphan'))

    item_id = db.Column(None, db.ForeignKey('item.id'))
    item = db.relationship(Item, backref=db.backref('line_items', cascade='all, delete-orphan'))

    quantity = db.Column(db.Integer, nullable=False)
    base_amount = db.Column(db.Float, default=0.0, nullable=False)
    discounted_amount = db.Column(db.Float, default=0.0, nullable=False)
    tax_amount = db.Column(db.Float, default=0.0, nullable=False)


class PaymentGateway(BaseNameMixin, db.Model):
    __tablename__ = 'payment_gateway'
    __uuid_primary_key__ = True
    data = db.Column(JsonDict, nullable=False, server_default='{}')


class Payment(IdMixin, db.Model):
    __tablename__ = 'payment'
    __uuid_primary_key__ = True
    payment_gateway_id = db.Column(None, db.ForeignKey('payment_gateway.id'))
    payment_gateway = db.relationship(PaymentGateway, backref=db.backref('payments', cascade='all, delete-orphan'))
    # Payment id issued by the payment gateway
    pg_payment_id = db.Column(db.Unicode(80), nullable=False)


class TRANSACTION_TYPES(LabeledEnum):
    REFUND = (0, __("Refund"))
    PAYMENT = (1, __("Payment"))


class Transaction(IdMixin, db.Model):
    """
    This model records transactions made with a customer.
    A transaction can either be of type 'Payment' or 'Refund',
    and may be associated with payment_id
        :balance stores the remaining balance in the user's account
    """
    __tablename__ = 'transaction'
    __uuid_primary_key__ = True

    order_id = db.Column(None, db.ForeignKey('order.id'), nullable=False)
    order = db.relationship(Order, backref=db.backref('transactions', cascade='all, delete-orphan'))
    amount = db.Column(db.Float, default=0.0, nullable=False)
    user_id = db.Column(None, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship(User, backref=db.backref('transactions', cascade='all, delete-orphan'))
    payment_id = db.Column(None, db.ForeignKey('payment.id'), nullable=False)
    payment = db.relationship(Payment, backref=db.backref('transactions', cascade='all, delete-orphan'))

    transaction_type = db.Column(db.Integer, nullable=False)
    balance = db.Column(db.Float, default=0.0, nullable=False)
