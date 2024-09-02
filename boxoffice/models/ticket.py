from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, ClassVar, NamedTuple
from uuid import UUID

from sqlalchemy.ext.hybrid import hybrid_property

from baseframe import _
from coaster.sqlalchemy import JsonDict, Query, role_check, with_roles
from coaster.utils import utcnow

from . import (
    AppenderQuery,
    BaseScopedNameMixin,
    DynamicMapped,
    Mapped,
    Model,
    UuidMixin,
    db,
    markdown_column,
    relationship,
    sa,
    timestamptz,
    timestamptz_now,
)
from .category import Category
from .discount_policy import item_discount_policy
from .enums import LineItemStatus
from .user import User

__all__ = ['Ticket', 'Price']


class AvailabilityData(NamedTuple):
    title: str
    quantity_total: int
    line_item_count: int


class Ticket(UuidMixin, BaseScopedNameMixin[UUID, User], Model):
    __tablename__ = 'item'

    description = markdown_column('description', default='', nullable=False)
    seq: Mapped[int]
    menu_id: Mapped[UUID] = sa.orm.mapped_column(
        'item_collection_id', sa.ForeignKey('item_collection.id')
    )
    menu: Mapped[Menu] = relationship(back_populates='tickets')
    parent: Mapped[Menu] = sa.orm.synonym('menu')
    category_id: Mapped[int] = sa.orm.mapped_column(sa.ForeignKey('category.id'))
    category: Mapped[Category] = relationship(back_populates='tickets')
    quantity_total: Mapped[int] = sa.orm.mapped_column(default=0)
    discount_policies: DynamicMapped[DiscountPolicy] = relationship(
        secondary=item_discount_policy,  # type: ignore[has-type]
        lazy='dynamic',
        back_populates='tickets',
    )
    assignee_details: Mapped[dict] = sa.orm.mapped_column(
        JsonDict,
        nullable=False,
        server_default=sa.text("'{}'::jsonb"),
    )
    event_date: Mapped[date | None]
    cancellable_until: Mapped[timestamptz | None]
    transferable_until: Mapped[timestamptz | None]
    restricted_entry: Mapped[bool] = sa.orm.mapped_column(default=False)
    # ISO 3166-2 code. Eg: KA for Karnataka
    place_supply_state_code: Mapped[str | None] = sa.orm.mapped_column(sa.Unicode(3))
    # ISO country code
    place_supply_country_code: Mapped[str | None] = sa.orm.mapped_column(sa.Unicode(2))
    prices: Mapped[list[Price]] = relationship(cascade='all, delete-orphan')
    line_items: DynamicMapped[LineItem] = relationship(
        cascade='all, delete-orphan', lazy='dynamic', back_populates='ticket'
    )

    __table_args__ = (sa.UniqueConstraint(menu_id, 'name'),)
    __roles__: ClassVar = {
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

    @role_check('item_owner')
    def has_item_owner_role(self, actor: User | None, _anchors: Any = ()) -> bool:
        return (
            actor is not None
            and self.menu.organization.userid in actor.organizations_owned_ids()
        )

    def current_price(self) -> Price | None:
        """Return the current price object for a ticket."""
        return self.price_at(utcnow())

    def has_higher_price(self, current_price: Price) -> bool:
        """Check if ticket has a higher price than the given current price."""
        return Price.query.filter(
            Price.end_at > current_price.end_at,
            Price.ticket == self,
            Price.discount_policy_id.is_(None),
        ).notempty()

    def discounted_price(self, discount_policy: DiscountPolicy) -> Price | None:
        """Return the discounted price for a ticket."""
        return Price.query.filter(
            Price.ticket == self, Price.discount_policy == discount_policy
        ).one_or_none()

    def standard_prices(self) -> Query[Price]:
        return Price.query.filter(
            Price.ticket == self, Price.discount_policy_id.is_(None)
        ).order_by(Price.start_at.desc())

    def price_at(self, timestamp: datetime) -> Price | None:
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
    def get_by_category(cls, category: Category) -> Query[Ticket]:
        return cls.query.filter(Ticket.category == category).order_by(cls.seq)

    @hybrid_property
    def quantity_available(self) -> int:
        available_count = self.quantity_total - self.confirmed_line_items.count()
        return available_count if available_count > 0 else 0

    @property
    def is_available(self) -> bool:
        """
        Check if a ticket is available.

        Test: has a current price object and has a positive quantity_available
        """
        return bool(self.current_price() and self.quantity_available > 0)

    def is_cancellable(self) -> bool:
        return utcnow() < self.cancellable_until if self.cancellable_until else True

    @property
    def active_price(self) -> Decimal | None:
        current_price = self.current_price()
        return current_price.amount if current_price else None

    @property
    def confirmed_line_items(self) -> AppenderQuery[LineItem]:
        """Return a query object preset with a ticket's confirmed line items."""
        return self.line_items.filter(LineItem.status == LineItemStatus.CONFIRMED)

    @with_roles(call={'item_owner'})
    def sold_count(self) -> int:
        return self.confirmed_line_items.filter(LineItem.final_amount > 0).count()

    @with_roles(call={'item_owner'})
    def free_count(self) -> int:
        return self.confirmed_line_items.filter(LineItem.final_amount == 0).count()

    @with_roles(call={'item_owner'})
    def cancelled_count(self) -> int:
        return self.line_items.filter(
            LineItem.status == LineItemStatus.CANCELLED
        ).count()

    @with_roles(call={'item_owner'})
    def net_sales(self) -> Decimal:
        return (
            db.session.query(sa.func.sum(LineItem.final_amount))
            .filter(
                LineItem.ticket_id == self.id,
                LineItem.status == LineItemStatus.CONFIRMED,
            )
            .scalar()
        )

    @classmethod
    def get_availability(cls, item_ids: Iterable[UUID]) -> dict[str, AvailabilityData]:
        """
        Return an availability dict.

        {'ticket_id': ('ticket)title', 'quantity_total', 'line_item_count')}
        """
        items_dict = {}
        rows = (
            db.session.query(
                cls.id.label('id'),
                cls.title.label('title'),
                cls.quantity_total.label('quantity_total'),
                sa.func.count(cls.id).label('ticket_count'),
            )
            .join(LineItem)
            .filter(
                LineItem.ticket_id.in_(item_ids),
                LineItem.status == LineItemStatus.CONFIRMED,
            )
            .group_by(cls.id)
            .all()
        )
        for row in rows:
            items_dict[str(row.id)] = AvailabilityData(
                row.title, row.quantity_total, row.ticket_count
            )
        return items_dict

    def demand_curve(self) -> Sequence[sa.engine.Row[tuple[Decimal, int]]]:
        """Return demand curve data of sale price and number of sales at that price."""
        return db.session.execute(
            sa.select(LineItem.final_amount, sa.func.count())
            .select_from(LineItem)
            .where(
                LineItem.ticket_id == self.id,
                LineItem.final_amount > 0,
                LineItem.status == LineItemStatus.CONFIRMED,
            )
            .group_by(LineItem.final_amount)
            .order_by(LineItem.final_amount)
        ).fetchall()


class Price(UuidMixin, BaseScopedNameMixin[UUID, User], Model):
    __tablename__ = 'price'
    ticket_id: Mapped[UUID] = sa.orm.mapped_column('item_id', sa.ForeignKey('item.id'))
    ticket: Mapped[Ticket] = relationship(back_populates='prices')

    discount_policy_id: Mapped[UUID | None] = sa.orm.mapped_column(
        sa.ForeignKey('discount_policy.id')
    )
    discount_policy: Mapped[DiscountPolicy | None] = relationship(
        back_populates='prices'
    )

    parent: Mapped[Ticket] = sa.orm.synonym('ticket')
    start_at: Mapped[timestamptz_now] = sa.orm.mapped_column()
    end_at: Mapped[timestamptz] = sa.orm.mapped_column()
    amount: Mapped[Decimal] = sa.orm.mapped_column(default=Decimal(0))
    currency: Mapped[str] = sa.orm.mapped_column(sa.Unicode(3), default='INR')

    __table_args__ = (
        sa.UniqueConstraint(ticket_id, 'name'),
        sa.CheckConstraint(start_at < end_at, name='price_start_at_lt_end_at_check'),
        sa.UniqueConstraint(ticket_id, discount_policy_id),
    )

    __roles__: ClassVar = {
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

    @role_check('price_owner')
    def has_price_owner_role(self, actor: User | None, _anchors: Any = ()) -> bool:
        return (
            actor is not None
            and self.ticket.menu.organization.userid in actor.organizations_owned_ids()
        )

    @property
    def discount_policy_title(self) -> str | None:
        return self.discount_policy.title if self.discount_policy else None

    @with_roles(call={'price_owner'})
    def tense(self) -> str:
        now = utcnow()
        if self.end_at < now:
            return _("past")
        if self.start_at > now:
            return _("upcoming")
        return _("current")


# Tail imports
from .line_item import LineItem  # isort:skip

if TYPE_CHECKING:
    from .discount_policy import DiscountPolicy
    from .menu import Menu
