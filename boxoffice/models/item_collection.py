# -*- coding: utf-8 -*-

from flask import url_for
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
    tax_type = db.Column(db.Unicode(80), nullable=True, default=u'GST')

    @property
    def url_for(self):
        return url_for('admin_item_collection', ic_id=self.id)

    __roles__ = {
        'ic_owner': {
            'write': {},
            'read': {'id', 'name', 'title', 'url_for', 'description'}
        }
    }

    def roles_for(self, user=None, token=None):
        if not user and not token:
            return set()
        roles = super(ItemCollection, self).roles_for(user, token)
        if self.organization.userid in user.organizations_owned_ids():
            roles.add('ic_owner')
        return roles
