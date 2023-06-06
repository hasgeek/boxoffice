"""Category model."""

from __future__ import annotations

from typing import TYPE_CHECKING, List
from uuid import UUID

from . import BaseScopedNameMixin, Mapped, Model, relationship, sa

__all__ = ['Category']


class Category(BaseScopedNameMixin, Model):
    __tablename__ = 'category'
    __table_args__ = (
        sa.UniqueConstraint('item_collection_id', 'name'),
        sa.UniqueConstraint('item_collection_id', 'seq'),
    )

    menu_id: Mapped[UUID] = sa.orm.mapped_column(
        'item_collection_id', sa.ForeignKey('item_collection.id')
    )
    menu: Mapped[ItemCollection] = relationship(back_populates='categories')
    seq: Mapped[int]
    tickets: Mapped[List[Item]] = relationship(
        cascade='all, delete-orphan', back_populates='category'
    )
    parent: Mapped[ItemCollection] = sa.orm.synonym('menu')

    __roles__ = {'category_owner': {'read': {'id', 'name', 'title', 'menu_id'}}}

    def roles_for(self, actor=None, anchors=()):
        roles = super().roles_for(actor, anchors)
        if self.menu.organization.userid in actor.organizations_owned_ids():
            roles.add('category_owner')
        return roles


if TYPE_CHECKING:
    from .item import Item
    from .item_collection import ItemCollection
