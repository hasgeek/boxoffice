# -*- coding: utf-8 -*-

from ..models import db, JsonDict, BaseScopedNameMixin, Organization, MarkdownColumn

__all__ = ['ItemCollection']


class ItemCollection(BaseScopedNameMixin, db.Model):
    """
    Represents a collection of items or an inventory.
    """
    __tablename__ = 'item_collection'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('organization_id', 'name'),)

    description = MarkdownColumn('description', default=u'', nullable=False)
    details = db.Column(JsonDict, server_default='{}', nullable=False)

    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    organization = db.relationship(Organization, backref=db.backref('item_collections', cascade='all, delete-orphan'))
    parent = db.synonym('organization')
