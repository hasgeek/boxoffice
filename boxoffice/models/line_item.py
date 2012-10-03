from decimal import Decimal
from datetime import datetime

from flask import url_for

from boxoffice.models import db, BaseMixin
from boxoffice.models.category import Category
from boxoffice.models.order import Order

__all__ = ['LineItem']


class LineItem(BaseMixin, db.Model):
    """
    A LineItem is part of an invoice.
    Each line item carries an item category, quantity, charged amount, tax rate & line total.
    """
    __tablename__ = 'lineitem'
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    order = db.relation(Order, primaryjoin=order_id == Order.id,
        backref=db.backref('lineitems', cascade='all, delete-orphan'))

    #: Item category of this LineItem
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship(Category, primaryjoin=category_id == Category.id)

    quantity = db.Column(db.Integer, default=1, nullable=False)

    total = db.Column(db.Numeric(10, 2), nullable=True)

    def update_total(self):
        self.total = self.quantity * self.category.price_after_tax

    def dict(self):
        return self.__dict__

    def as_json(self):
        return {
            'event': self.category.event.title,
            'category_id': self.category_id,
            'category_desc': self.category.title,
            'quantity': self.quantity,
            'pat': self.category.price_after_tax,
            'tax_rate': self.category.tax_rate,
            'created_at': self.created_at.isoformat() + 'Z',
            'updated_at': self.updated_at.isoformat() + 'Z',
        }
