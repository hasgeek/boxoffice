from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional, Sequence, Tuple
from uuid import UUID

from sqlalchemy.ext.hybrid import hybrid_property

from baseframe import _
from coaster.sqlalchemy import with_roles
from coaster.utils import utcnow

from . import (
    BaseScopedNameMixin,
    DynamicMapped,
    Mapped,
    MarkdownColumn,
    Model,
    db,
    jsonb_dict,
    relationship,
    sa,
    timestamptz,
)
from .category import Category
from .discount_policy import item_discount_policy

__all__ = ['Item', 'Price']


class Item(BaseScopedNameMixin, Model):
    __tablename__ = 'item'
    __uuid_primary_key__ = True
    __table_args__ = (sa.UniqueConstraint('item_collection_id', 'name'),)

    description = MarkdownColumn('description', default='', nullable=False)
    seq: Mapped[int]
    menu_id: Mapped[UUID] = sa.orm.mapped_column(
        'item_collection_id', sa.ForeignKey('item_collection.id')
    )
    menu: Mapped[ItemCollection] = relationship(back_populates='tickets')
    parent: Mapped[ItemCollection] = sa.orm.synonym('menu')
    category_id: Mapped[int] = sa.orm.mapped_column(sa.ForeignKey('category.id'))
    category: Mapped[Category] = relationship(back_populates='tickets')
    quantity_total: Mapped[int] = sa.orm.mapped_column(default=0)
    discount_policies: DynamicMapped[DiscountPolicy] = relationship(
        secondary=item_discount_policy, lazy='dynamic', back_populates='tickets'
    )
    assignee_details: Mapped[jsonb_dict]
    event_date: Mapped[Optional[date]]
    cancellable_until: Mapped[Optional[timestamptz]]
    transferable_until: Mapped[Optional[timestamptz]]
    restricted_entry: Mapped[bool] = sa.orm.mapped_column(default=False)
    # ISO 3166-2 code. Eg: KA for Karnataka
    place_supply_state_code: Mapped[Optional[str]] = sa.orm.mapped_column(sa.Unicode(3))
    # ISO country code
    place_supply_country_code: Mapped[Optional[str]] = sa.orm.mapped_column(
        sa.Unicode(2)
    )
    prices: Mapped[List[Price]] = relationship(cascade='all, delete-orphan')
    line_items: DynamicMapped[LineItem] = relationship(
        cascade='all, delete-orphan', lazy='dynamic', back_populates='ticket'
    )

    __roles__ = {
        'item_owner': {
            'read': {
                'id',
                'title',
                'description_text',
                'description_html',
                'quantity_total',
                'quantity_available',
                'active_price',
                'assignee_details',
            }
        }
    }

    def roles_for(self, actor=None, anchors=()):
        roles = super().roles_for(actor, anchors)
        if self.menu.organization.userid in actor.organizations_owned_ids():
            roles.add('item_owner')
        return roles

    def current_price(self):
        """Return the current price object for a ticket."""
        return self.price_at(utcnow())

    def has_higher_price(self, current_price):
        """Check if ticket has a higher price than the given current price."""
        return Price.query.filter(
            Price.end_at > current_price.end_at,
            Price.ticket == self,
            Price.discount_policy_id.is_(None),
        ).notempty()

    def discounted_price(self, discount_policy):
        """Return the discounted price for a ticket."""
        return Price.query.filter(
            Price.ticket == self, Price.discount_policy == discount_policy
        ).one_or_none()

    def standard_prices(self):
        return Price.query.filter(
            Price.ticket == self, Price.discount_policy_id.is_(None)
        ).order_by(Price.start_at.desc())

    def price_at(self, timestamp):
        """Return the price object for a ticket at a given time."""
        return (
            Price.query.filter(
                Price.ticket == self,
                Price.start_at <= timestamp,
                Price.end_at > timestamp,
                Price.discount_policy_id.is_(None),
            )
            .order_by(Price.created_at.desc())
            .first()
        )

    @classmethod
    def get_by_category(cls, category):
        return cls.query.filter(Item.category == category).order_by(cls.seq)

    @hybrid_property
    def quantity_available(self):
        available_count = self.quantity_total - self.confirmed_line_items.count()
        return available_count if available_count > 0 else 0

    @property
    def is_available(self):
        """
        Check if a ticket is available.

        Test: has a current price object and has a positive quantity_available
        """
        return bool(self.current_price() and self.quantity_available > 0)

    def is_cancellable(self):
        return utcnow() < self.cancellable_until if self.cancellable_until else True

    @property
    def active_price(self):
        current_price = self.current_price()
        return current_price.amount if current_price else None

    @property
    def confirmed_line_items(self):
        """Return a query object preset with a ticket's confirmed line items."""
        return self.line_items.filter(LineItem.status == LINE_ITEM_STATUS.CONFIRMED)

    @with_roles(call={'item_owner'})
    def sold_count(self):
        return self.confirmed_line_items.filter(LineItem.final_amount > 0).count()

    @with_roles(call={'item_owner'})
    def free_count(self):
        return self.confirmed_line_items.filter(LineItem.final_amount == 0).count()

    @with_roles(call={'item_owner'})
    def cancelled_count(self):
        return self.line_items.filter(
            LineItem.status == LINE_ITEM_STATUS.CANCELLED
        ).count()

    @with_roles(call={'item_owner'})
    def net_sales(self) -> Decimal:
        return (
            db.session.query(sa.func.sum(LineItem.final_amount))
            .filter(
                LineItem.ticket_id == self.id,
                LineItem.status == LINE_ITEM_STATUS.CONFIRMED,
            )
            .first()[0]
        )

    @classmethod
    def get_availability(cls, item_ids):
        """
        Return an availability dict.

        {'ticket_id': ('ticket)title', 'quantity_total', 'line_item_count')}
        """
        items_dict = {}
        item_tups = (
            db.session.query(
                cls.id, cls.title, cls.quantity_total, sa.func.count(cls.id)
            )
            .join(LineItem)
            .filter(
                LineItem.ticket_id.in_(item_ids),
                LineItem.status == LINE_ITEM_STATUS.CONFIRMED,
            )
            .group_by(cls.id)
            .all()
        )
        for item_tup in item_tups:
            items_dict[str(item_tup[0])] = item_tup[1:]
        return items_dict

    def demand_curve(self) -> Sequence[sa.engine.Row[Tuple[Decimal, int]]]:
        """Return demand curve data of sale price and number of sales at that price."""
        return db.session.execute(
            sa.select(LineItem.final_amount, sa.func.count())
            .select_from(LineItem)
            .where(
                LineItem.ticket_id == self.id,
                LineItem.final_amount > 0,
                LineItem.status == LINE_ITEM_STATUS.CONFIRMED,
            )
            .group_by(LineItem.final_amount)
            .order_by(LineItem.final_amount)
        ).fetchall()


class Price(BaseScopedNameMixin, Model):
    __tablename__ = 'price'
    __uuid_primary_key__ = True
    __table_args__ = (
        sa.UniqueConstraint('item_id', 'name'),
        sa.CheckConstraint('start_at < end_at', 'price_start_at_lt_end_at_check'),
        sa.UniqueConstraint('item_id', 'discount_policy_id'),
    )

    ticket_id: Mapped[UUID] = sa.orm.mapped_column('item_id', sa.ForeignKey('item.id'))
    ticket: Mapped[Item] = relationship(back_populates='prices')

    discount_policy_id: Mapped[Optional[UUID]] = sa.orm.mapped_column(
        sa.ForeignKey('discount_policy.id')
    )
    discount_policy: Mapped[Optional[DiscountPolicy]] = relationship(
        back_populates='prices'
    )

    parent: Mapped[Item] = sa.orm.synonym('ticket')
    start_at: Mapped[timestamptz] = sa.orm.mapped_column(default=sa.func.utcnow())
    end_at: Mapped[timestamptz]
    amount: Mapped[Decimal] = sa.orm.mapped_column(default=Decimal(0))
    currency: Mapped[str] = sa.orm.mapped_column(sa.Unicode(3), default='INR')

    __roles__ = {
        'price_owner': {
            'read': {
                'id',
                'ticket_id',
                'start_at',
                'end_at',
                'amount',
                'currency',
                'discount_policy_title',
            }
        }
    }

    def roles_for(self, actor=None, anchors=()):
        roles = super().roles_for(actor, anchors)
        if self.ticket.menu.organization.userid in actor.organizations_owned_ids():
            roles.add('price_owner')
        return roles

    @property
    def discount_policy_title(self):
        return self.discount_policy.title if self.discount_policy else None

    @with_roles(call={'price_owner'})
    def tense(self):
        now = utcnow()
        if self.end_at < now:
            return _("past")
        if self.start_at > now:
            return _("upcoming")
        return _("current")


# Tail imports
from .line_item import LINE_ITEM_STATUS, LineItem  # isort:skip

if TYPE_CHECKING:
    from .discount_policy import DiscountPolicy
    from .item_collection import ItemCollection
