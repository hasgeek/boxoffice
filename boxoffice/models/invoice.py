# -*- coding: utf-8 -*-

from boxoffice.models import db, BaseMixin, Order, PaymentTransaction


__all__ = ['Invoice']


class Invoice(BaseMixin, db.Model):
    __tablename__ = 'invoice'
    __uuid_primary_key__ = True

    invoicee_name = db.Column(db.Unicode(255), nullable=True)
    street_address = db.Column(db.Unicode(255), nullable=True)
    city = db.Column(db.Unicode(255), nullable=True)
    state = db.Column(db.Unicode(255), nullable=True)
    country = db.Column(db.Unicode(255), nullable=True)
    postcode = db.Column(db.Unicode(255), nullable=True)
    # GSTIN in the case of India
    taxid = db.Column(db.Unicode(255), nullable=True)

    customer_order_id = db.Column(None, db.ForeignKey('customer_order.id'), nullable=False, index=True, unique=False)
    order = db.relationship(Order, backref=db.backref('invoice', cascade='all, delete-orphan'))
