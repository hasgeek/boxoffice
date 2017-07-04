# -*- coding: utf-8 -*-

from decimal import Decimal
from boxoffice.models import db, BaseMixin
from baseframe import __
from coaster.utils import LabeledEnum

__all__ = ['Invoice', 'InvoiceLineItem']


class ITEM_TYPE(LabeledEnum):
    GOOD = (0, __("Good"))
    SERVICE = (1, __("Service"))


class Invoice(BaseMixin, db.Model):
    __tablename__ = 'invoice'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('organization_id', 'invoice_no'),)

    invoicee_name = db.Column(db.Unicode(255), nullable=True)
    invoicee_email = db.Column(db.Unicode(254), nullable=True)
    invoice_no = db.Column(db.Unicode(32), nullable=True)
    invoiced_at = db.Column(db.DateTime, nullable=True)
    street_address = db.Column(db.Unicode(255), nullable=True)
    city = db.Column(db.Unicode(255), nullable=True)
    state = db.Column(db.Unicode(255), nullable=True)
    country = db.Column(db.Unicode(255), nullable=True)
    postcode = db.Column(db.Unicode(8), nullable=True)
    # GSTIN in the case of India
    taxid = db.Column(db.Unicode(255), nullable=True)
    # India specific: this is the state short code. Eg: KA for Karnataka
    place_of_supply = db.Column(db.Unicode(3), nullable=True)

    customer_order_id = db.Column(None, db.ForeignKey('customer_order.id'), nullable=False, index=True, unique=False)
    order = db.relationship('Order', backref=db.backref('invoices', cascade='all, delete-orphan'))

    organization_id = db.Column(None, db.ForeignKey('organization.id'), nullable=False)
    organization = db.relationship('Organization', backref=db.backref('invoices', cascade='all, delete-orphan', lazy='dynamic'))


class InvoiceLineItem(BaseMixin, db.Model):
    __tablename__ = 'invoice_line_item'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('invoice_id', 'seq'),)

    seq = db.Column(db.Integer, nullable=False)
    item_title = db.Column(db.Unicode(255), nullable=False)
    # In India, this will be GST
    tax_type = db.Column(db.Unicode(255), nullable=False)
    item_type = db.Column(db.Integer, default=ITEM_TYPE.SERVICE, nullable=False)
    discount_title = db.Column(db.Unicode(255), nullable=False)

    currency = db.Column(db.Unicode(3), nullable=False)
    base_amount = db.Column(db.Numeric, default=Decimal(0), nullable=False)
    discounted_amount = db.Column(db.Numeric, default=Decimal(0), nullable=False)
    final_amount = db.Column(db.Numeric, default=Decimal(0), nullable=False)

    invoice_id = db.Column(None, db.ForeignKey('invoice.id'), nullable=False, index=True, unique=False)
    invoice = db.relationship(Invoice, backref=db.backref('line_items', cascade='all, delete-orphan'))
