from boxoffice.models import db, BaseScopedNameMixin
from boxoffice.models import ItemCollection

__all__ = ['Category']


class Category(BaseScopedNameMixin, db.Model):
    __tablename__ = 'category'
    __table_args__ = (db.UniqueConstraint('item_collection_id', 'name'),)

    item_collection_id = db.Column(None, db.ForeignKey('item_collection.id'), nullable=False)
    item_collection = db.relationship(ItemCollection, backref=db.backref('categories', cascade='all, delete-orphan'))

    parent = db.synonym('item_collection')
