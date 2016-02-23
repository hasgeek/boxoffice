from boxoffice.models import db, BaseScopedNameMixin
from boxoffice.models import ItemCollection

__all__ = ['Category']


class Category(BaseScopedNameMixin, db.Model):
    __tablename__ = 'category'
    __tableargs__ = (db.UniqueConstraint('item_collection_id', 'name'),)

    item_collection_id = db.Column(None,
                                   db.ForeignKey('item_collection.id'),
                                   nullable=False)
    item_collection = db.relationship(ItemCollection,
                                      backref=db.backref('categories', cascade='all, delete-orphan'))  # noqa

    parent = db.synonym('item_collection')

    def __repr__(self):
        return '<Category "{category}" in "{item_collection}">'.format(category=self.title,
            item_collection=self.item_collection.title)
