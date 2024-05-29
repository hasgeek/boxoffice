"""Category model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar
from uuid import UUID

from coaster.sqlalchemy import role_check

from . import BaseScopedNameMixin, Mapped, Model, relationship, sa
from .user import User

__all__ = ['Category']


class Category(BaseScopedNameMixin[int, User], Model):
    __tablename__ = 'category'

    menu_id: Mapped[UUID] = sa.orm.mapped_column(
        'item_collection_id', sa.ForeignKey('item_collection.id')
    )
    menu: Mapped[Menu] = relationship(back_populates='categories')
    seq: Mapped[int]
    tickets: Mapped[list[Ticket]] = relationship(
        cascade='all, delete-orphan', back_populates='category'
    )
    parent: Mapped[Menu] = sa.orm.synonym('menu')

    __table_args__ = (
        sa.UniqueConstraint('item_collection_id', 'name'),
        sa.UniqueConstraint('item_collection_id', 'seq'),
    )
    __roles__: ClassVar = {
        'category_owner': {'read': {'id', 'name', 'title', 'menu_id'}}
    }

    @role_check('category_owner')
    def has_category_owner_role(self, actor: User | None, _anchors: Any = ()) -> bool:
        return (
            actor is not None
            and self.menu.organization.userid in actor.organizations_owned_ids()
        )


if TYPE_CHECKING:
    from .menu import Menu
    from .ticket import Ticket
