from boxoffice.models import db, BaseNameMixin, BaseScopedNameMixin
from boxoffice.models import Inventory, Category
from boxoffice.models.discount_policy import item_discount_policy

__all__ = ['Item']


class Item(BaseScopedNameMixin, db.Model):
    __tablename__ = 'item'
    __uuid_primary_key__ = True
    __tableargs__ = (db.UniqueConstraint('inventory_id', 'name'), db.CheckConstraint('quantity_available <= quantity_total', 'quantity_bound'))

    description = db.Column(db.Unicode(2500), nullable=False)

    inventory_id = db.Column(None, db.ForeignKey('inventory.id'), nullable=False)
    inventory = db.relationship(Inventory,
        backref=db.backref('items', cascade='all, delete-orphan'))
    parent = db.synonym('inventory')

    category_id = db.Column(None, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship(Category,
        backref=db.backref('items', cascade='all, delete-orphan'))

    quantity_available = db.Column(db.Integer, default=0, nullable=False)
    quantity_total = db.Column(db.Integer, default=0, nullable=False)

    discount_policies = db.relationship('DiscountPolicy', secondary=item_discount_policy)

    def __repr__(self):
        return u'<Item "{item}" in "{inventory}">'.format(item=self.title, inventory=self.inventory.title)
