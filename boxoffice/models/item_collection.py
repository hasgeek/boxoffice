# -*- coding: utf-8 -*-

from ..models import db, BaseScopedNameMixin, Organization, MarkdownColumn

__all__ = ['ItemCollection']


class ItemCollection(BaseScopedNameMixin, db.Model):
    """
    Represents a collection of items or an inventory.
    """
    __tablename__ = 'item_collection'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('organization_id', 'name'),)

    description = MarkdownColumn('description', default=u'', nullable=False)

    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    organization = db.relationship(Organization, backref=db.backref('item_collections', cascade='all, delete-orphan'))
    parent = db.synonym('organization')

    __roles__ = {
        'description': {
            'write': {'item_collection_owner'},
            'read': {'item_collection_owner'}
        }
    }

    def roles(self, user=None, inherited=None, token=None):
        roles = super(ItemCollection, self).roles(user, inherited, token)
        if user or token:
            roles.add('user')
        if user:
            roles.add('item_collection_owner')
        return roles
