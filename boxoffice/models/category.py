from boxoffice.models import db, BaseScopedNameMixin
from boxoffice.models import Inventory

__all__ = ['Category']


class Category(BaseScopedNameMixin, db.Model):
    __tablename__ = 'category'
    __uuid_primary_key__ = True
    __tableargs__ = (db.UniqueConstraint('inventory_id', 'name'))

    inventory_id = db.Column(None, db.ForeignKey('inventory.id'), nullable=False)
    inventory = db.relationship(Inventory,
      backref=db.backref('categories', cascade='all, delete-orphan'))

    parent = db.synonym('inventory')

    def __repr__(self):
        return u'<Category "{category}" in "{inventory}">'.format(category=self.title, inventory=self.inventory.title)
