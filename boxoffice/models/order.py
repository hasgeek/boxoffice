# -*- coding: utf-8 -*-

from decimal import Decimal
from datetime import datetime
from collections import namedtuple
from sqlalchemy import sql
from boxoffice.models import db, BaseMixin, User
from coaster.utils import LabeledEnum, buid
from baseframe import __

__all__ = ['Order', 'ORDER_STATUS']


class ORDER_STATUS(LabeledEnum):
    PURCHASE_ORDER = (0, __("Purchase Order"))
    SALES_ORDER = (1, __("Sales Order"))
    INVOICE = (2, __("Invoice"))
    CANCELLED = (3, __("Cancelled Order"))

ORDER_STATUS.CONFIRMED = [ORDER_STATUS.SALES_ORDER, ORDER_STATUS.INVOICE]


def get_latest_invoice_no(organization):
    """
    Returns the last invoice number used, 0 if no order has ben invoiced yet.
    """
    last_invoice_no = db.session.query(sql.functions.max(Order.invoice_no))\
        .filter(Order.organization == organization).first()
    return last_invoice_no[0] if last_invoice_no[0] else 0


def order_amounts_ntuple(base_amount, discounted_amount, final_amount):
    order_amounts = namedtuple('OrderAmounts', ['base_amount', 'discounted_amount', 'final_amount'])
    return order_amounts(base_amount, discounted_amount, final_amount)


class Order(BaseMixin, db.Model):
    __tablename__ = 'customer_order'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('organization_id', 'invoice_no'),
        db.UniqueConstraint('access_token'))

    user_id = db.Column(None, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship(User, backref=db.backref('orders', cascade='all, delete-orphan'))
    item_collection_id = db.Column(None, db.ForeignKey('item_collection.id'), nullable=False)
    item_collection = db.relationship('ItemCollection', backref=db.backref('orders', cascade='all, delete-orphan', lazy='dynamic'))

    organization_id = db.Column(None, db.ForeignKey('organization.id'), nullable=False)
    organization = db.relationship('Organization', backref=db.backref('orders', cascade='all, delete-orphan', lazy='dynamic'))

    status = db.Column(db.Integer, default=ORDER_STATUS.PURCHASE_ORDER, nullable=False)

    initiated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime, nullable=True)
    invoiced_at = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)

    access_token = db.Column(db.Unicode(22), nullable=False, default=buid)

    buyer_email = db.Column(db.Unicode(254), nullable=False)
    buyer_fullname = db.Column(db.Unicode(80), nullable=False)
    buyer_phone = db.Column(db.Unicode(16), nullable=False)

    invoice_no = db.Column(db.Integer, nullable=True)

    def confirm_sale(self):
        """Updates the status to ORDER_STATUS.SALES_ORDER"""
        for line_item in self.line_items:
            line_item.confirm()
        self.invoice_no = get_latest_invoice_no(self.organization) + 1
        self.status = ORDER_STATUS.SALES_ORDER
        self.paid_at = datetime.utcnow()

    def invoice(self):
        """Sets invoiced_at, status"""
        for line_item in self.line_items:
            line_item.confirm()
        self.invoiced_at = datetime.utcnow()
        self.status = ORDER_STATUS.INVOICE

    def get_amounts(self):
        """
        Calculates and returns the order's base_amount, discounted_amount and
        final_amount as a namedtuple
        """
        base_amount = Decimal(0)
        discounted_amount = Decimal(0)
        final_amount = Decimal(0)
        for line_item in self.line_items:
            base_amount += line_item.base_amount
            discounted_amount += line_item.discounted_amount
            final_amount += line_item.final_amount
        return order_amounts_ntuple(base_amount, discounted_amount, final_amount)

    @property
    def is_confirmed(self):
        return self.status in ORDER_STATUS.CONFIRMED

    def is_fully_assigned(self):
        """Checks if all the line items in an order have an assignee"""
        for line_item in self.get_confirmed_line_items:
            if not line_item.current_assignee:
                return False
        return True
