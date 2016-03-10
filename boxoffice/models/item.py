from boxoffice.models import db, BaseScopedNameMixin
from boxoffice.models import ItemCollection, Category
from boxoffice.models.discount_policy import item_discount_policy

__all__ = ['Item']


class Item(BaseScopedNameMixin, db.Model):
    __tablename__ = 'item'
    __uuid_primary_key__ = True
    __tableargs__ = (db.UniqueConstraint('item_collection_id', 'name'),
        db.CheckConstraint('quantity_available <= quantity_total',
                          'item_quantity_available_lte_quantity_total_check'))

    description = db.Column(db.Unicode(2500), nullable=False)

    item_collection_id = db.Column(None,
                                   db.ForeignKey('item_collection.id'),
                                   nullable=False)
    item_collection = db.relationship(ItemCollection,
                                      backref=db.backref('items', cascade='all, delete-orphan'))  # noqa
    parent = db.synonym('item_collection')

    category_id = db.Column(None, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship(Category,
                               backref=db.backref('items', cascade='all, delete-orphan'))  # noqa

    quantity_available = db.Column(db.Integer, default=0, nullable=False)
    quantity_total = db.Column(db.Integer, default=0, nullable=False)

    discount_policies = db.relationship('DiscountPolicy', secondary=item_discount_policy, lazy='dynamic')

    def __repr__(self):
        return u'<Item "{item}" in "{item_collection}">'.format(item=self.title,
            item_collection=self.item_collection.title)
