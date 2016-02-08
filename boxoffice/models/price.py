from boxoffice.models import db, BaseNameMixin, Item
from datetime import datetime

__all__ = ['Price']


class Price(BaseNameMixin, db.Model):
    __tablename__ = 'price'
    __uuid_primary_key__ = True

    item_id = db.Column(None, db.ForeignKey('item.id'), nullable=False)
    item = db.relationship(Item, backref=db.backref('prices', cascade='all, delete-orphan'))
    valid_from = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    valid_upto = db.Column(db.DateTime, nullable=False)

    amount = db.Column(db.Numeric, default=0.0, nullable=False)
    currency = db.Column(db.Unicode(3), nullable=False, default=u'INR')
    __table_args__ = (db.CheckConstraint('valid_from < valid_upto', 'valid_bound'),)

    def __repr__(self):
        return u'<Price "{price}" for item "{item}">'.format(price=self.title, item=self.item.title)


    @classmethod
    def current(cls, item):
        now = datetime.utcnow()
        return cls.query.filter(cls.item == item, cls.valid_from <= now, cls.valid_upto >= now).order_by('created_at desc').first()
