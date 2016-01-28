from boxoffice.models import db, BaseNameMixin, Item
from datetime import datetime

__all__ = ['Price']


class Price(BaseNameMixin, db.Model):
    __tablename__ = 'price'
    __uuid_primary_key__ = True

    item_id = db.Column(None, db.ForeignKey('item.id'), nullable=False)
    item = db.relationship(Item, backref=db.backref('prices', cascade='all, delete-orphan'))
    valid_from = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    valid_upto = db.Column(db.DateTime, nullable=True)

    amount = db.Column(db.Float, default=0.0, nullable=False)
    __table_args__ = (db.CheckConstraint('valid_from < valid_upto', 'valid_bound'), db.CheckConstraint('amount >= 0', 'amount_bound_lower'))
