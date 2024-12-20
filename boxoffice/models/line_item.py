from __future__ import annotations

from collections import OrderedDict
from collections.abc import Sequence
from datetime import date, datetime, timedelta, tzinfo
from decimal import Decimal
from typing import TYPE_CHECKING, NamedTuple, cast
from uuid import UUID

from flask import current_app
from isoweek import Week
from typing_extensions import TypedDict

from baseframe import localize_timezone
from coaster.sqlalchemy import JsonDict
from coaster.utils import isoweek_datetime, midnight_to_utc, utcnow

from . import (
    BaseMixin,
    DynamicMapped,
    Mapped,
    Model,
    UuidMixin,
    db,
    relationship,
    sa,
    timestamptz,
)
from .enums import LineItemStatus
from .user import User

__all__ = ['Assignee', 'LineItem', 'LineItemTuple']


class LineItemTuple(NamedTuple):
    """Duck-type for LineItem."""

    id: UUID | None
    ticket_id: UUID
    base_amount: Decimal | None
    discount_policy_id: UUID | None = None
    discount_coupon_id: UUID | None = None
    discounted_amount: Decimal | None = Decimal(0)
    final_amount: Decimal | None = None


class LineItemDict(TypedDict):
    ticket_id: str


class Assignee(BaseMixin[int, User], Model):
    __tablename__ = 'assignee'
    # lastuser id
    user_id: Mapped[int | None] = sa.orm.mapped_column(sa.ForeignKey('user.id'))
    user: Mapped[User | None] = relationship(back_populates='assignees')
    line_item_id: Mapped[UUID] = sa.orm.mapped_column(sa.ForeignKey('line_item.id'))
    line_item: Mapped[LineItem] = relationship(back_populates='assignees')
    fullname: Mapped[str] = sa.orm.mapped_column(sa.Unicode(80))
    #: Unvalidated email address
    email: Mapped[str] = sa.orm.mapped_column(sa.Unicode(254))
    #: Unvalidated phone number
    phone: Mapped[str | None] = sa.orm.mapped_column(sa.Unicode(16))
    details: Mapped[dict] = sa.orm.mapped_column(JsonDict, default={})
    current: Mapped[bool | None] = sa.orm.mapped_column()

    __table_args__ = (
        sa.UniqueConstraint(line_item_id, current),
        sa.CheckConstraint(current.isnot(False), 'assignee_current_check'),
    )


class LineItem(UuidMixin, BaseMixin[UUID, User], Model):
    """
    A line item in a sale receipt.

    As financial records, line items cannot ever be deleted. They must only be marked
    as cancelled.
    """

    __tablename__ = 'line_item'
    # line_item_seq is the relative number of the line item per order.
    line_item_seq: Mapped[int] = sa.orm.mapped_column()
    customer_order_id: Mapped[UUID] = sa.orm.mapped_column(
        sa.ForeignKey('customer_order.id'), index=True, unique=False
    )
    order: Mapped[Order] = relationship(back_populates='line_items')
    ticket_id: Mapped[UUID] = sa.orm.mapped_column(
        'item_id', sa.ForeignKey('item.id'), index=True, unique=False
    )
    ticket: Mapped[Ticket] = relationship(back_populates='line_items')
    previous_id: Mapped[UUID | None] = sa.orm.mapped_column(
        sa.ForeignKey('line_item.id'), unique=True
    )
    previous: Mapped[LineItem] = relationship(
        back_populates='revision',
        remote_side='LineItem.id',
        uselist=False,
    )
    revision: Mapped[LineItem] = relationship(uselist=False, back_populates='previous')
    discount_policy_id: Mapped[UUID | None] = sa.orm.mapped_column(
        sa.ForeignKey('discount_policy.id'), index=True, unique=False
    )
    discount_policy: Mapped[DiscountPolicy | None] = relationship(
        back_populates='line_items'
    )

    discount_coupon_id: Mapped[UUID | None] = sa.orm.mapped_column(
        sa.ForeignKey('discount_coupon.id'), index=True, unique=False
    )
    discount_coupon: Mapped[DiscountCoupon | None] = relationship(
        back_populates='line_items'
    )

    base_amount: Mapped[Decimal] = sa.orm.mapped_column(default=Decimal(0))
    discounted_amount: Mapped[Decimal] = sa.orm.mapped_column(default=Decimal(0))
    final_amount: Mapped[Decimal] = sa.orm.mapped_column(sa.Numeric, default=Decimal(0))
    status: Mapped[int] = sa.orm.mapped_column(default=LineItemStatus.PURCHASE_ORDER)
    ordered_at: Mapped[timestamptz | None]
    cancelled_at: Mapped[timestamptz | None]
    assignees: DynamicMapped[Assignee] = relationship(
        cascade='all, delete-orphan', lazy='dynamic', back_populates='line_item'
    )

    __table_args__ = (sa.UniqueConstraint(customer_order_id, line_item_seq),)

    def permissions(self, actor: User, inherited: set[str] | None = None) -> set[str]:
        perms = super().permissions(actor, inherited)
        if self.order.organization.userid in actor.organizations_owned_ids():
            perms.add('org_admin')
        return perms

    @classmethod
    def calculate(
        cls,
        line_items: Sequence[LineItem | LineItemDict],
        coupons: Sequence[str] | None = None,
    ) -> Sequence[LineItemTuple]:
        """
        Return line item data tuples.

        For each line item, returns a tuple of base_amount, discounted_amount,
        final_amount, discount_policy and discount coupon populated
        """
        base_amount: Decimal | None
        item_line_items: dict[str, list[LineItemTuple]] = {}
        calculated_line_items: list[LineItemTuple] = []
        coupon_list = list(set(coupons)) if coupons else []
        discounter = LineItemDiscounter()

        # make named tuples for line items,
        # assign the base_amount for each of them, None if a ticket is unavailable
        for line_item in line_items:
            ticket: Ticket | None
            if isinstance(line_item, LineItem):
                ticket = line_item.ticket
                base_amount = line_item.base_amount
                line_item_id = line_item.id
            else:
                ticket = Ticket.query.get(line_item['ticket_id'])
                if ticket is None:
                    continue
                current_price = ticket.current_price()
                base_amount = (
                    current_price.amount
                    if current_price is not None and ticket.is_available
                    else None
                )
                line_item_id = None

            if not item_line_items.get(str(ticket.id)):
                item_line_items[str(ticket.id)] = []
            item_line_items[str(ticket.id)].append(
                LineItemTuple(
                    id=line_item_id,
                    ticket_id=ticket.id,
                    base_amount=base_amount,
                )
            )

        for item_value in item_line_items.values():
            calculated_line_items.extend(
                discounter.get_discounted_line_items(item_value, coupon_list)
            )

        return calculated_line_items

    def confirm(self) -> None:
        self.status = LineItemStatus.CONFIRMED

    assignee: Mapped[Assignee | None] = relationship(
        Assignee,
        primaryjoin='and_'
        '(Assignee.line_item_id == LineItem.id,'
        ' Assignee.current.is_(True))',
        uselist=False,
        viewonly=True,
    )

    # TODO: assignee = relationship(Assignee, primaryjoin=Assignee.line_item ==
    # self and Assignee.current.is_(True), uselist=False) Don't use "current_assignee"
    # -- we want to imply that there can only be one assignee and the rest are
    # historical (and hence not 'assignees')
    @property
    def current_assignee(self) -> Assignee | None:
        return self.assignees.filter(Assignee.current.is_(True)).one_or_none()

    @property
    def is_transferable(self) -> bool:
        tz = current_app.config['tz']
        now = localize_timezone(utcnow(), tz)
        if self.assignee is None:
            return True  # first time assignment has no deadline for now
        return (
            now < localize_timezone(self.ticket.transferable_until, tz)
            if self.ticket.transferable_until is not None
            else (
                now.date() <= self.ticket.event_date
                if self.ticket.event_date is not None
                else True
            )
        )

    @property
    def is_confirmed(self) -> bool:
        return self.status == LineItemStatus.CONFIRMED

    @property
    def is_cancelled(self) -> bool:
        return self.status == LineItemStatus.CANCELLED

    @property
    def is_free(self) -> bool:
        return self.final_amount == Decimal('0')

    def cancel(self) -> None:
        """Set status and cancelled_at."""
        self.status = LineItemStatus.CANCELLED
        self.cancelled_at = sa.func.utcnow()

    def make_void(self) -> None:
        self.status = LineItemStatus.VOID
        self.cancelled_at = sa.func.utcnow()

    def is_cancellable(self) -> bool:
        tz = current_app.config['tz']
        now = localize_timezone(utcnow(), tz)
        return self.is_confirmed and (
            now < localize_timezone(self.ticket.cancellable_until, tz)
            if self.ticket.cancellable_until
            else True
        )

    @classmethod
    def get_max_seq(cls, order: Order) -> int:
        return (
            db.session.query(sa.func.max(LineItem.line_item_seq))
            .filter(LineItem.order == order)
            .scalar()
        )


def counts_per_date_per_item(menu: Menu, user_tz: tzinfo) -> dict[date, dict[str, int]]:
    """
    Return number of line items sold per date per ticket.

    Eg: {'2016-01-01': {'item-xxx': 20}}
    """
    date_ticket_counts: dict[date, dict[str, int]] = {}
    for ticket in menu.tickets:
        ticket_id = str(ticket.id)

        lineitem_results = db.session.execute(
            sa.select(
                sa.cast(
                    sa.func.date_trunc(
                        'day', sa.func.timezone(user_tz, LineItem.ordered_at)
                    ),
                    sa.Date,
                ).label('date'),
                sa.func.count().label('count'),
            )
            .select_from(LineItem)
            .where(
                LineItem.ticket_id == ticket.id,
                LineItem.status == LineItemStatus.CONFIRMED,
            )
            .group_by('date')
            .order_by('date')
        ).all()
        for date_count in lineitem_results:
            if not date_ticket_counts.get(date_count.date):
                # if this date hasn't been been mapped in date_item_counts yet
                date_ticket_counts[date_count.date] = {
                    ticket_id: cast(int, date_count.count)
                }
            else:
                # if it has been mapped, assign the count
                date_ticket_counts[date_count.date][ticket_id] = cast(
                    int, date_count.count
                )
    return date_ticket_counts


def sales_by_date(
    sales_datetime: date | datetime, ticket_ids: Sequence[str], user_tz: tzinfo
) -> Decimal | None:
    """
    Return the sales amount accrued during the day.

    Requires a date or datetime, list of ticket_ids and timezone.
    """
    if not ticket_ids:
        return None

    start_at = midnight_to_utc(sales_datetime, timezone=user_tz)
    end_at = midnight_to_utc(sales_datetime + timedelta(days=1), timezone=user_tz)
    sales_on_date = cast(
        Decimal,
        db.session.scalar(
            sa.select(sa.func.sum(LineItem.final_amount))
            .select_from(LineItem)
            .where(
                LineItem.status == LineItemStatus.CONFIRMED,
                LineItem.ordered_at >= start_at,
                LineItem.ordered_at < end_at,
                LineItem.ticket_id.in_(ticket_ids),
            )
        ),
    )
    return sales_on_date if sales_on_date else Decimal(0)


def calculate_weekly_sales(
    menu_ids: Sequence[str | UUID], user_tz: str | tzinfo, year: int
) -> OrderedDict[int, int]:
    """Calculate weekly sales for a year in the given menu_ids."""
    ordered_week_sales = OrderedDict()
    for year_week in Week.weeks_of_year(year):
        ordered_week_sales[year_week.week] = 0
    start_at = isoweek_datetime(year, 1, user_tz)
    end_at = isoweek_datetime(year + 1, 1, user_tz)

    week_sales = db.session.execute(
        sa.select(
            sa.func.extract(
                'WEEK',
                sa.func.timezone(user_tz, sa.func.timezone('UTC', LineItem.ordered_at)),
            ).label('sales_week'),
            sa.func.sum(LineItem.final_amount).label('sum'),
        )
        .select_from(LineItem)
        .join(Ticket, LineItem.ticket_id == Ticket.id)
        .where(
            LineItem.status.in_(
                [LineItemStatus.CONFIRMED.value, LineItemStatus.CANCELLED.value]
            ),
            Ticket.menu_id.in_(menu_ids),
            sa.func.timezone(user_tz, sa.func.timezone('UTC', LineItem.ordered_at))
            >= start_at,
            sa.func.timezone(user_tz, sa.func.timezone('UTC', LineItem.ordered_at))
            < end_at,
        )
        .group_by('sales_week')
        .order_by('sales_week')
    ).all()

    for week_sale in week_sales:
        ordered_week_sales[int(week_sale.sales_week)] = week_sale.sum

    return ordered_week_sales


def sales_delta(user_tz: tzinfo, ticket_ids: Sequence[str]) -> Decimal:
    """Calculate the percentage difference in sales between today and yesterday."""
    today = utcnow().date()
    yesterday = today - timedelta(days=1)
    today_sales = sales_by_date(today, ticket_ids, user_tz)
    yesterday_sales = sales_by_date(yesterday, ticket_ids, user_tz)
    if not today_sales or not yesterday_sales:
        return Decimal('0')
    return round(Decimal('100') * (today_sales - yesterday_sales) / yesterday_sales, 2)


# Tail import
from .ticket import Ticket  # isort:skip
from .line_item_discounter import LineItemDiscounter  # isort:skip

if TYPE_CHECKING:
    from .discount_policy import DiscountCoupon, DiscountPolicy
    from .menu import Menu
    from .order import Order
