from decimal import Decimal
from boxoffice.models import db, BaseScopedNameMixin
from boxoffice.models.event import Event

__all__ = ['Category', 'CATEGORY_STATUS', 'CATEGORY_STATUS_CODES']

class CATEGORY_STATUS:
	DRAFT = 1
	LIVE = 2
	EXPIRED = 3

CATEGORY_STATUS_CODES = [
    [1, "Draft"],
    [2, "Live"],
    [3, "Expired"]
]

class Category(BaseScopedNameMixin, db.Model):
    """
    Categories are classes of items that can be purchased, along with inventory available, unit price and tax rate
    Categories can be in Draft, Live or Expired state.
    """
    __tablename__ = 'category'

    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    event = db.relation(Event, backref=db.backref('categories', cascade='all, delete-orphan'))
    parent = db.synonym('event')
    
    nos_available = db.Column(db.Integer, default=0, nullable=False)
    price_after_tax = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.0'))
    tax_rate = db.Column(db.Numeric(2, 2), nullable=False, default=Decimal('0.0'))
    status = db.Column(db.Integer, default=CATEGORY_STATUS.DRAFT, nullable=False)

    __table_args__ = (db.UniqueConstraint('name', 'event_id'),)

    def price_before_tax(self):
        return self.price_after_tax / (1 + self.tax_rate/100)

    @classmethod
    def get_by_event(cls, event):
        return cls.query.filter_by(event=event)

    @classmethod
    def get_by_status(cls, status):
        return cls.query.filter_by(status=status)        

    @classmethod
    def get_by_event_and_status(cls, event, status):
        return cls.query.filter_by(event=event, status=status)