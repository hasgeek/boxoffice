from boxoffice.models import db, BaseNameMixin
from boxoffice.models.category import Category
from boxoffice.models.event import event_item

__all__ = ['Item']


class Item(BaseNameMixin, db.Model):
    """
    An item is a single type of inventory
    """
    __tablename__ = 'item'
    __uuid_primary_key__ = True

    description = db.Column(db.Unicode(2500), default=u'', nullable=True)

    category_id = db.Column(None, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship(Category, primaryjoin=category_id == Category.id)

    quantity_available = db.Column(db.Integer, default=0, nullable=False)
    quantity_total = db.Column(db.Integer, default=0, nullable=False)

    events = db.relationship('Event', secondary=event_item)
