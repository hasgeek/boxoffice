from __future__ import annotations

from collections import OrderedDict, namedtuple
from datetime import timedelta
from decimal import Decimal
from typing import List, Optional, overload

from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.sql import func

from flask import current_app

from isoweek import Week
from typing_extensions import Literal

from baseframe import __, localize_timezone
from coaster.utils import LabeledEnum, isoweek_datetime, midnight_to_utc, utcnow

from . import BaseMixin, JsonDict, db
from .order import Order

__all__ = ['LineItem', 'LINE_ITEM_STATUS', 'Assignee']


class LINE_ITEM_STATUS(LabeledEnum):  # NOQA: N801
    CONFIRMED = (0, __("Confirmed"))
    CANCELLED = (1, __("Cancelled"))
    PURCHASE_ORDER = (2, __("Purchase Order"))
    #: A line item can be made void by the system to invalidate
    #: a line item. Eg: a discount no longer applicable on a line item as a result of a cancellation
    VOID = (3, __("Void"))
    TRANSACTION = {CONFIRMED, VOID, CANCELLED}


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


class Assignee(BaseMixin, db.Model):
    __tablename__ = 'assignee'
    __table_args__ = (
        db.UniqueConstraint('line_item_id', 'current'),
        db.CheckConstraint("current != '0'", 'assignee_current_check'),
    )

    # lastuser id
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship(
        'User', backref=db.backref('assignees', cascade='all, delete-orphan')
    )

    line_item_id = db.Column(None, db.ForeignKey('line_item.id'), nullable=False)
    line_item = db.relationship(
        'LineItem',
        backref=db.backref('assignees', cascade='all, delete-orphan', lazy='dynamic'),
    )

    fullname = db.Column(db.Unicode(80), nullable=False)
    #: Unvalidated email address
    email = db.Column(db.Unicode(254), nullable=False)
    #: Unvalidated phone number
    phone = db.Column(db.Unicode(16), nullable=True)
    details = db.Column(JsonDict, nullable=False, default={})
    current = db.Column(db.Boolean, nullable=True)


class LineItem(BaseMixin, db.Model):
    """
    A line item in a sale receipt.

    As financial records, line items cannot ever be deleted. They must only be marked
    as cancelled.

    TODO: Rename this model to `Ticket`
    """

    __tablename__ = 'line_item'
    __uuid_primary_key__ = True
    __table_args__ = (
        db.UniqueConstraint('customer_order_id', 'line_item_seq'),
        db.UniqueConstraint('previous_id'),
    )

    # line_item_seq is the relative number of the line item per order.
    line_item_seq = db.Column(db.Integer, nullable=False)
    customer_order_id = db.Column(
        None,
        db.ForeignKey('customer_order.id'),
        nullable=False,
        index=True,
        unique=False,
    )
    order = db.relationship(
        Order,
        backref=db.backref(
            'line_items',
            cascade='all, delete-orphan',
            order_by=line_item_seq,
            collection_class=ordering_list('line_item_seq', count_from=1),
        ),
    )

    item_id = db.Column(
        None, db.ForeignKey('item.id'), nullable=False, index=True, unique=False
    )
    item = db.relationship(
        'Item',
        backref=db.backref('line_items', cascade='all, delete-orphan', lazy='dynamic'),
    )

    previous_id = db.Column(
        None, db.ForeignKey('line_item.id'), nullable=True, unique=True
    )
    previous = db.relationship(
        'LineItem',
        primaryjoin='line_item.c.id==line_item.c.previous_id',
        backref=db.backref('revision', uselist=False),
        remote_side='LineItem.id',
    )

    discount_policy_id = db.Column(
        None,
        db.ForeignKey('discount_policy.id'),
        nullable=True,
        index=True,
        unique=False,
    )
    discount_policy = db.relationship(
        'DiscountPolicy', backref=db.backref('line_items', lazy='dynamic')
    )

    discount_coupon_id = db.Column(
        None,
        db.ForeignKey('discount_coupon.id'),
        nullable=True,
        index=True,
        unique=False,
    )
    discount_coupon = db.relationship(
        'DiscountCoupon', backref=db.backref('line_items')
    )

    base_amount = db.Column(db.Numeric, default=Decimal(0), nullable=False)
    discounted_amount = db.Column(db.Numeric, default=Decimal(0), nullable=False)
    final_amount = db.Column(db.Numeric, default=Decimal(0), nullable=False)
    status = db.Column(
        db.Integer, default=LINE_ITEM_STATUS.PURCHASE_ORDER, nullable=False
    )
    ordered_at = db.Column(db.TIMESTAMP(timezone=True), nullable=True)
    cancelled_at = db.Column(db.TIMESTAMP(timezone=True), nullable=True)

    def permissions(self, user, inherited=None):
        perms = super().permissions(user, inherited)
        if self.order.organization.userid in user.organizations_owned_ids():
            perms.add('org_admin')
        return perms

    @overload
    @classmethod
    def calculate(
        cls,
        line_items: List[LineItem],
        realculate: Literal[True],
        coupons: Optional[List[str]] = None,
    ): ...

    @overload
    @classmethod
    def calculate(
        cls,
        line_items: List[dict],
        realculate: Literal[False],
        coupons: Optional[List[str]] = None,
    ): ...

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

        for item_id in item_line_items.keys():
            calculated_line_items.extend(
                discounter.get_discounted_line_items(
                    item_line_items[item_id], coupon_list
                )
            )

        return calculated_line_items

    def confirm(self):
        self.status = LINE_ITEM_STATUS.CONFIRMED

    # TODO: assignee = db.relationship(Assignee, primaryjoin=Assignee.line_item == self and Assignee.current.is_(True), uselist=False)
    # Don't use current_assignee -- we want to imply that there can only be one assignee and the rest are historical (and hence not 'assignees')
    @property
    def current_assignee(self):
        return self.assignees.filter(Assignee.current.is_(True)).one_or_none()

    @property
    def is_transferable(self):
        tz = current_app.config['tz']
        now = localize_timezone(utcnow(), tz)
        if self.current_assignee is None:
            return True  # first time assignment has no deadline for now
        else:
            return (
                now < localize_timezone(self.item.transferable_until, tz)
                if self.item.transferable_until is not None
                else (
                    now.date() <= self.item.event_date
                    if self.item.event_date is not None
                    else True
                )
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
        self.cancelled_at = func.utcnow()

    def make_void(self):
        self.status = LINE_ITEM_STATUS.VOID
        self.cancelled_at = func.utcnow()

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
            db.session.query(func.max(LineItem.line_item_seq))
            .filter(LineItem.order == order)
            .scalar()
        )


Order.confirmed_line_items = db.relationship(
    LineItem,
    lazy='dynamic',
    primaryjoin=db.and_(
        LineItem.customer_order_id == Order.id,
        LineItem.status == LINE_ITEM_STATUS.CONFIRMED,
    ),
    viewonly=True,
)


Order.confirmed_and_cancelled_line_items = db.relationship(
    LineItem,
    lazy='dynamic',
    primaryjoin=db.and_(
        LineItem.customer_order_id == Order.id,
        LineItem.status.in_([LINE_ITEM_STATUS.CONFIRMED, LINE_ITEM_STATUS.CANCELLED]),
    ),
    viewonly=True,
)


Order.initial_line_items = db.relationship(
    LineItem,
    lazy='dynamic',
    primaryjoin=db.and_(
        LineItem.customer_order_id == Order.id,
        LineItem.previous_id.is_(None),
        LineItem.status.in_(LINE_ITEM_STATUS.TRANSACTION),
    ),
    viewonly=True,
)


def counts_per_date_per_item(item_collection, user_tz):
    """
    Return number of line items sold per date per item.

    Eg: {'2016-01-01': {'item-xxx': 20}}
    """
    date_item_counts = {}
    for item in item_collection.items:
        item_id = str(item.id)
        item_results = (
            db.session.query(db.column('date'), db.column('count'))
            .from_statement(
                db.text(
                    '''SELECT DATE_TRUNC('day', line_item.ordered_at AT TIME ZONE :timezone)::date as date, count(line_item.id) AS count
            FROM line_item WHERE item_id = :item_id AND status = :status
            GROUP BY date ORDER BY date ASC'''
                )
            )
            .params(
                timezone=user_tz, status=LINE_ITEM_STATUS.CONFIRMED, item_id=item.id
            )
            .all()
        )
        for date_count in item_results:
            if not date_item_counts.get(date_count.date):
                # if this date hasn't been been mapped in date_item_counts yet
                date_item_counts[date_count.date] = {item_id: date_count.count}
            else:
                # if it has been mapped, assign the count
                date_item_counts[date_count.date][item_id] = date_count.count
    return date_item_counts


def sales_by_date(sales_datetime, item_ids, user_tz):
    """
    Return the sales amount accrued during the day.

    Requires a date or datetime, list of item_ids and timezone.
    """
    if not item_ids:
        return None

    start_at = midnight_to_utc(sales_datetime, timezone=user_tz)
    end_at = midnight_to_utc(sales_datetime + timedelta(days=1), timezone=user_tz)
    sales_on_date = (
        db.session.query(db.column('sum'))
        .from_statement(
            db.text(
                '''SELECT SUM(final_amount) FROM line_item
        WHERE status=:status AND ordered_at >= :start_at AND ordered_at < :end_at
        AND line_item.item_id IN :item_ids
        '''
            )
        )
        .params(
            status=LINE_ITEM_STATUS.CONFIRMED,
            start_at=start_at,
            end_at=end_at,
            item_ids=tuple(item_ids),
        )
        .scalar()
    )
    return sales_on_date if sales_on_date else Decimal(0)


def calculate_weekly_sales(item_collection_ids, user_tz, year):
    """Calculate weekly sales for a year in the given item_collection_ids."""
    ordered_week_sales = OrderedDict()
    for year_week in Week.weeks_of_year(year):
        ordered_week_sales[year_week.week] = 0
    start_at = isoweek_datetime(year, 1, user_tz)
    end_at = isoweek_datetime(year + 1, 1, user_tz)

    week_sales = (
        db.session.query(db.column('sales_week'), db.column('sum'))
        .from_statement(
            db.text(
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


def sales_delta(user_tz, item_ids):
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
