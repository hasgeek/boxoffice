from __future__ import annotations

from collections import OrderedDict, namedtuple
from datetime import date, datetime, timedelta, tzinfo
from decimal import Decimal
from typing import TYPE_CHECKING, Dict, List, Optional, Union, cast, overload
from uuid import UUID

from flask import current_app
from isoweek import Week
from typing_extensions import Literal

from baseframe import localize_timezone
from coaster.utils import isoweek_datetime, midnight_to_utc, utcnow

from . import BaseMixin, DynamicMapped, Mapped, Model, db, jsonb, relationship, sa
from .enums import LINE_ITEM_STATUS
from .order import Order

__all__ = ['LineItem', 'Assignee']


LineItemTuple = namedtuple(
    'LineItemTuple',
    [
        'item_id',
        'id',
        'base_amount',
        'discount_policy_id',
        'discount_coupon_id',
        'discounted_amount',
        'final_amount',
    ],
)


def make_ntuple(item_id, base_amount, **kwargs):
    return LineItemTuple(
        item_id,
        kwargs.get('line_item_id', None),
        base_amount,
        kwargs.get('discount_policy_id', None),
        kwargs.get('discount_coupon_id', None),
        kwargs.get('discounted_amount', Decimal(0)),
        kwargs.get('final_amount', None),
    )


class Assignee(BaseMixin, Model):
    __tablename__ = 'assignee'
    __table_args__ = (
        sa.UniqueConstraint('line_item_id', 'current'),
        sa.CheckConstraint("current != '0'", 'assignee_current_check'),
    )

    # lastuser id
    user_id: Mapped[Optional[int]] = sa.orm.mapped_column(
        sa.ForeignKey('user.id'), nullable=True
    )
    user: Mapped[Optional[User]] = relationship(back_populates='assignees')

    line_item_id: Mapped[UUID] = sa.orm.mapped_column(
        sa.ForeignKey('line_item.id'), nullable=False
    )
    line_item: Mapped[LineItem] = relationship(back_populates='assignees')

    fullname = sa.orm.mapped_column(sa.Unicode(80), nullable=False)
    #: Unvalidated email address
    email = sa.orm.mapped_column(sa.Unicode(254), nullable=False)
    #: Unvalidated phone number
    phone = sa.orm.mapped_column(sa.Unicode(16), nullable=True)
    details: Mapped[jsonb] = sa.orm.mapped_column(nullable=False, default={})
    current = sa.orm.mapped_column(sa.Boolean, nullable=True)


class LineItem(BaseMixin, Model):
    """
    A line item in a sale receipt.

    As financial records, line items cannot ever be deleted. They must only be marked
    as cancelled.

    TODO: Rename this model to `Ticket`
    """

    __tablename__ = 'line_item'
    __uuid_primary_key__ = True
    __table_args__ = (
        sa.UniqueConstraint('customer_order_id', 'line_item_seq'),
        sa.UniqueConstraint('previous_id'),
    )

    # line_item_seq is the relative number of the line item per order.
    line_item_seq: Mapped[int] = sa.orm.mapped_column(nullable=False)
    customer_order_id: Mapped[UUID] = sa.orm.mapped_column(
        sa.ForeignKey('customer_order.id'), nullable=False, index=True, unique=False
    )
    order: Mapped[Order] = relationship(back_populates='line_items')
    item_id: Mapped[UUID] = sa.orm.mapped_column(
        sa.ForeignKey('item.id'), nullable=False, index=True, unique=False
    )
    item: Mapped[Item] = relationship(back_populates='line_items')
    previous_id: Mapped[UUID] = sa.orm.mapped_column(
        sa.ForeignKey('line_item.id'), nullable=True, unique=True
    )
    previous: Mapped[LineItem] = relationship(
        # primaryjoin='line_item.c.id==line_item.c.previous_id',
        back_populates='revision',
        remote_side='LineItem.id',
        # foreign_keys=[previous_id],
        uselist=False,
    )
    revision: Mapped[LineItem] = relationship(uselist=False, back_populates='previous')
    discount_policy_id: Mapped[UUID] = sa.orm.mapped_column(
        sa.ForeignKey('discount_policy.id'), nullable=True, index=True, unique=False
    )
    discount_policy: Mapped[DiscountPolicy] = relationship(back_populates='line_items')

    discount_coupon_id: Mapped[UUID] = sa.orm.mapped_column(
        sa.ForeignKey('discount_coupon.id'), nullable=True, index=True, unique=False
    )
    discount_coupon: Mapped[DiscountCoupon] = relationship(back_populates='line_items')

    base_amount: Mapped[Decimal] = sa.orm.mapped_column(
        default=Decimal(0), nullable=False
    )
    discounted_amount: Mapped[Decimal] = sa.orm.mapped_column(
        default=Decimal(0), nullable=False
    )
    final_amount: Mapped[Decimal] = sa.orm.mapped_column(
        sa.Numeric, default=Decimal(0), nullable=False
    )
    status: Mapped[int] = sa.orm.mapped_column(
        default=LINE_ITEM_STATUS.PURCHASE_ORDER, nullable=False
    )
    ordered_at: Mapped[datetime] = sa.orm.mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=True
    )
    cancelled_at: Mapped[datetime] = sa.orm.mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=True
    )
    assignees: DynamicMapped[Assignee] = relationship(
        cascade='all, delete-orphan', lazy='dynamic', back_populates='line_item'
    )

    def permissions(self, actor, inherited=None):
        perms = super().permissions(actor, inherited)
        if self.order.organization.userid in actor.organizations_owned_ids():
            perms.add('org_admin')
        return perms

    @overload
    @classmethod
    def calculate(
        cls,
        line_items: List[LineItem],
        realculate: Literal[True],
        coupons: Optional[List[str]] = None,
    ):
        ...

    @overload
    @classmethod
    def calculate(
        cls,
        line_items: List[dict],
        realculate: Literal[False],
        coupons: Optional[List[str]] = None,
    ):
        ...

    # TODO: Fix this classmethod's typing
    @classmethod
    def calculate(cls, line_items, recalculate=False, coupons=None):
        """
        Return line item data tuples.

        For each line item, returns a tuple of base_amount, discounted_amount,
        final_amount, discount_policy and discount coupon populated

        If the `recalculate` flag is set to `True`, the line_items will be considered
        as SQLAlchemy objects.
        """
        item_line_items = {}
        calculated_line_items = []
        coupon_list = list(set(coupons)) if coupons else []
        discounter = LineItemDiscounter()

        # make named tuples for line items,
        # assign the base_amount for each of them, None if an item is unavailable
        for line_item in line_items:
            if recalculate:
                item = line_item.item
                # existing line item, use the original base amount
                base_amount = line_item.base_amount
                line_item_id = line_item.id
            else:
                item = Item.query.get(line_item['item_id'])
                # new line item, use the current price
                base_amount = item.current_price().amount if item.is_available else None
                line_item_id = None

            if not item_line_items.get(str(item.id)):
                item_line_items[str(item.id)] = []
            item_line_items[str(item.id)].append(
                make_ntuple(
                    item_id=item.id, base_amount=base_amount, line_item_id=line_item_id
                )
            )

        for item_value in item_line_items.values():
            calculated_line_items.extend(
                discounter.get_discounted_line_items(item_value, coupon_list)
            )

        return calculated_line_items

    def confirm(self):
        self.status = LINE_ITEM_STATUS.CONFIRMED

    # TODO: assignee = relationship(Assignee, primaryjoin=Assignee.line_item ==
    # self and Assignee.current.is_(True), uselist=False) Don't use "current_assignee"
    # -- we want to imply that there can only be one assignee and the rest are
    # historical (and hence not 'assignees')
    @property
    def current_assignee(self):
        return self.assignees.filter(Assignee.current.is_(True)).one_or_none()

    @property
    def is_transferable(self):
        tz = current_app.config['tz']
        now = localize_timezone(utcnow(), tz)
        if self.current_assignee is None:
            return True  # first time assignment has no deadline for now
        return (
            now < localize_timezone(self.item.transferable_until, tz)
            if self.item.transferable_until is not None
            else now.date() <= self.item.event_date
            if self.item.event_date is not None
            else True
        )

    @property
    def is_confirmed(self):
        return self.status == LINE_ITEM_STATUS.CONFIRMED

    @property
    def is_cancelled(self):
        return self.status == LINE_ITEM_STATUS.CANCELLED

    @property
    def is_free(self):
        return self.final_amount == Decimal('0')

    def cancel(self):
        """Set status and cancelled_at."""
        self.status = LINE_ITEM_STATUS.CANCELLED
        self.cancelled_at = sa.func.utcnow()

    def make_void(self):
        self.status = LINE_ITEM_STATUS.VOID
        self.cancelled_at = sa.func.utcnow()

    def is_cancellable(self):
        tz = current_app.config['tz']
        now = localize_timezone(utcnow(), tz)
        return self.is_confirmed and (
            now < localize_timezone(self.item.cancellable_until, tz)
            if self.item.cancellable_until
            else True
        )

    @classmethod
    def get_max_seq(cls, order):
        return (
            db.session.query(sa.func.max(LineItem.line_item_seq))
            .filter(LineItem.order == order)
            .scalar()
        )


Order.confirmed_line_items = relationship(
    LineItem,
    lazy='dynamic',
    primaryjoin=sa.and_(
        LineItem.customer_order_id == Order.id,
        LineItem.status == LINE_ITEM_STATUS.CONFIRMED,
    ),
    viewonly=True,
)


Order.confirmed_and_cancelled_line_items = relationship(
    LineItem,
    lazy='dynamic',
    primaryjoin=sa.and_(
        LineItem.customer_order_id == Order.id,
        LineItem.status.in_([LINE_ITEM_STATUS.CONFIRMED, LINE_ITEM_STATUS.CANCELLED]),
    ),
    viewonly=True,
)


Order.initial_line_items = relationship(
    LineItem,
    lazy='dynamic',
    primaryjoin=sa.and_(
        LineItem.customer_order_id == Order.id,
        LineItem.previous_id.is_(None),
        LineItem.status.in_(LINE_ITEM_STATUS.TRANSACTION),
    ),
    viewonly=True,
)


def counts_per_date_per_item(
    item_collection: ItemCollection, user_tz: tzinfo
) -> Dict[str, Dict[str, int]]:
    """
    Return number of line items sold per date per item.

    Eg: {'2016-01-01': {'item-xxx': 20}}
    """
    date_item_counts: Dict[str, Dict[str, int]] = {}
    for item in item_collection.items:
        item_id = str(item.id)

        item_results = db.session.execute(
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
                LineItem.item_id == item.id,
                LineItem.status == LINE_ITEM_STATUS.CONFIRMED,
            )
            .group_by('date')
            .order_by('date')
        ).all()
        for date_count in item_results:
            if not date_item_counts.get(date_count.date):
                # if this date hasn't been been mapped in date_item_counts yet
                date_item_counts[date_count.date] = {item_id: date_count.count}
            else:
                # if it has been mapped, assign the count
                date_item_counts[date_count.date][item_id] = date_count.count
    return date_item_counts


def sales_by_date(
    sales_datetime: Union[date, datetime], item_ids: List[str], user_tz: tzinfo
) -> Optional[Decimal]:
    """
    Return the sales amount accrued during the day.

    Requires a date or datetime, list of item_ids and timezone.
    """
    if not item_ids:
        return None

    start_at = midnight_to_utc(sales_datetime, timezone=user_tz)
    end_at = midnight_to_utc(sales_datetime + timedelta(days=1), timezone=user_tz)
    sales_on_date = cast(
        Decimal,
        db.session.scalar(
            sa.select(sa.func.sum(LineItem.final_amount))
            .select_from(LineItem)
            .where(
                LineItem.status == LINE_ITEM_STATUS.CONFIRMED,
                LineItem.ordered_at >= start_at,
                LineItem.ordered_at < end_at,
                LineItem.item_id.in_(item_ids),
            )
        ),
    )
    return sales_on_date if sales_on_date else Decimal(0)


def calculate_weekly_sales(item_collection_ids: List[str], user_tz: tzinfo, year: int):
    """Calculate weekly sales for a year in the given item_collection_ids."""
    ordered_week_sales = OrderedDict()
    for year_week in Week.weeks_of_year(year):
        ordered_week_sales[year_week.week] = 0
    start_at = isoweek_datetime(year, 1, user_tz)
    end_at = isoweek_datetime(year + 1, 1, user_tz)

    week_sales = (
        db.session.query(sa.column('sales_week'), sa.column('sum'))
        .from_statement(
            sa.text(
                '''
        SELECT EXTRACT(WEEK FROM ordered_at AT TIME ZONE 'UTC' AT TIME ZONE :timezone)
        AS sales_week, SUM(final_amount) AS sum
        FROM line_item INNER JOIN item on line_item.item_id = item.id
        WHERE status IN :statuses AND item_collection_id IN :item_collection_ids
        AND ordered_at AT TIME ZONE 'UTC' AT TIME ZONE :timezone >= :start_at
        AND ordered_at AT TIME ZONE 'UTC' AT TIME ZONE :timezone < :end_at
        GROUP BY sales_week ORDER BY sales_week;
        '''
            )
        )
        .params(
            timezone=user_tz,
            statuses=(LINE_ITEM_STATUS.CONFIRMED, LINE_ITEM_STATUS.CANCELLED),
            start_at=start_at,
            end_at=end_at,
            item_collection_ids=tuple(item_collection_ids),
        )
        .all()
    )

    for week_sale in week_sales:
        ordered_week_sales[int(week_sale.sales_week)] = week_sale.sum

    return ordered_week_sales


def sales_delta(user_tz: tzinfo, item_ids: List[str]):
    """Calculate the percentage difference in sales between today and yesterday."""
    today = utcnow().date()
    yesterday = today - timedelta(days=1)
    today_sales = sales_by_date(today, item_ids, user_tz)
    yesterday_sales = sales_by_date(yesterday, item_ids, user_tz)
    if not today_sales or not yesterday_sales:
        return 0
    return round(Decimal('100') * (today_sales - yesterday_sales) / yesterday_sales, 2)


# Tail import
from .item import Item  # isort:skip
from .line_item_discounter import LineItemDiscounter  # isort:skip

if TYPE_CHECKING:
    from .discount_policy import DiscountCoupon, DiscountPolicy
    from .item_collection import ItemCollection
    from .user import User
