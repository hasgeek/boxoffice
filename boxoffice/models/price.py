import decimal
from boxoffice.models import db, BaseScopedNameMixin, Item
from datetime import datetime

__all__ = ['Price']


class Price(BaseScopedNameMixin, db.Model):
    __tablename__ = 'price'
    __uuid_primary_key__ = True
    __tableargs__ = (db.UniqueConstraint('item_id', 'name'),
        db.CheckConstraint('valid_from < valid_to', 'price_valid_from_lte_valid_to_check'))

    item_id = db.Column(None, db.ForeignKey('item.id'), nullable=False)
    item = db.relationship(Item, backref=db.backref('prices', cascade='all, delete-orphan'))
    parent = db.synonym('item')
    valid_from = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    valid_upto = db.Column(db.DateTime, nullable=False)

    amount = db.Column(db.Numeric, default=decimal.Decimal(0), nullable=False)
    currency = db.Column(db.Unicode(3), nullable=False, default=u'INR')

    @classmethod
    def current(cls, item):
        """
        Returns the current price for an item
        """
        return cls.at(item, datetime.utcnow())

    @classmethod
    def at(cls, item, timestamp):
        """
        Returns the price for an item at a given time
        """
        return cls.query.filter(cls.item == item, cls.valid_from <= timestamp, cls.valid_upto >= timestamp)\
            .order_by('created_at desc').first()
