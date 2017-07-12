# -*- coding: utf-8 -*-

from boxoffice.models import db, BaseScopedNameMixin
from boxoffice.models import ItemCollection
from sqlalchemy.ext.orderinglist import ordering_list

__all__ = ['Category']


class Category(BaseScopedNameMixin, db.Model):
    __tablename__ = 'category'
    __table_args__ = (db.UniqueConstraint('item_collection_id', 'name'), db.UniqueConstraint('item_collection_id', 'seq'))

    item_collection_id = db.Column(None, db.ForeignKey('item_collection.id'), nullable=False)
    seq = db.Column(db.Integer, nullable=False)
    item_collection = db.relationship(ItemCollection,
        backref=db.backref('categories', cascade='all, delete-orphan',
            order_by=seq, collection_class=ordering_list('seq', count_from=1)))
    parent = db.synonym('item_collection')

    __roles__ = {
        'category_owner': {
            'write': {},
            'read': {'id', 'name', 'title'}
        }
    }

    def roles_for(self, user=None, token=None):
        if not user and not token:
            return set()
        roles = super(Category, self).roles_for(user, token)
        if user or token:
            roles.add('user')
        if self.item_collection.organization.userid in user.organizations_owned_ids():
            roles.add('category_owner')
        return roles
