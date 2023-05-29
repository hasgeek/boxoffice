"""Category model."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.orderinglist import ordering_list

from . import BaseScopedNameMixin, Mapped, Model, backref, relationship, sa

__all__ = ['Category']


class Category(BaseScopedNameMixin, Model):
    __tablename__ = 'category'
    __table_args__ = (
        sa.UniqueConstraint('item_collection_id', 'name'),
        sa.UniqueConstraint('item_collection_id', 'seq'),
    )

    item_collection_id: Mapped[UUID] = sa.orm.mapped_column(
        sa.ForeignKey('item_collection.id'), nullable=False
    )
    seq = sa.Column(sa.Integer, nullable=False)
    item_collection = relationship(
        'ItemCollection',
        backref=backref(
            'categories',
            cascade='all, delete-orphan',
            order_by=seq,
            collection_class=ordering_list('seq', count_from=1),
        ),
    )
    parent = sa.orm.synonym('item_collection')

    __roles__ = {
        'category_owner': {'read': {'id', 'name', 'title', 'item_collection_id'}}
    }

    def roles_for(self, actor=None, anchors=()):
        roles = super().roles_for(actor, anchors)
        if self.item_collection.organization.userid in actor.organizations_owned_ids():
            roles.add('category_owner')
        return roles
