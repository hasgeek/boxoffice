from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.orderinglist import ordering_list

from baseframe import _, __
from coaster.sqlalchemy import with_roles
from coaster.utils import LabeledEnum, utcnow

from . import (
    BaseScopedNameMixin,
    Mapped,
    MarkdownColumn,
    Model,
    backref,
    db,
    jsonb_dict,
    relationship,
    sa,
)
from .category import Category
from .discount_policy import item_discount_policy

__all__ = ['Item', 'Price']


class GST_TYPE(LabeledEnum):  # noqa: N801
    GOOD = (0, __("Good"))
    SERVICE = (1, __("Service"))


class Item(BaseScopedNameMixin, Model):
    __tablename__ = 'item'
    __uuid_primary_key__ = True
    __table_args__ = (sa.UniqueConstraint('item_collection_id', 'name'),)

    description = MarkdownColumn('description', default='', nullable=False)
    seq = sa.Column(sa.Integer, nullable=False)

    item_collection_id: Mapped[UUID] = sa.orm.mapped_column(
        sa.ForeignKey('item_collection.id'), nullable=False
    )
    item_collection = relationship(
        'ItemCollection',
        backref=backref(
            'items',
            cascade='all, delete-orphan',
            order_by=seq,
            collection_class=ordering_list('seq', count_from=1),
        ),
    )

    parent = sa.orm.synonym('item_collection')

    category_id: Mapped[int] = sa.orm.mapped_column(
        sa.ForeignKey('category.id'), nullable=False
    )
    category = relationship(
        Category, backref=backref('items', cascade='all, delete-orphan')
    )

    quantity_total = sa.Column(sa.Integer, default=0, nullable=False)

    discount_policies = relationship(
        'DiscountPolicy',
        secondary=item_discount_policy,  # type: ignore[has-type]
        backref='items',
        lazy='dynamic',
    )

    assignee_details: Mapped[jsonb_dict] = sa.orm.mapped_column()

    event_date = sa.Column(sa.Date, nullable=True)

    cancellable_until = sa.Column(sa.TIMESTAMP(timezone=True), nullable=True)

    transferable_until = sa.Column(sa.TIMESTAMP(timezone=True), nullable=True)

    restricted_entry = sa.Column(sa.Boolean, default=False, nullable=False)
    # ISO 3166-2 code. Eg: KA for Karnataka
    place_supply_state_code = sa.Column(sa.Unicode(3), nullable=True)
    # ISO country code
    place_supply_country_code = sa.Column(sa.Unicode(2), nullable=True)

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
        if self.item_collection.organization.userid in actor.organizations_owned_ids():
            roles.add('item_owner')
        return roles

    def current_price(self):
        """Return the current price object for an item."""
        return self.price_at(utcnow())

    def has_higher_price(self, current_price):
        """Check if item has a higher price than the given current price."""
        return Price.query.filter(
            Price.end_at > current_price.end_at,
            Price.item == self,
            Price.discount_policy_id.is_(None),
        ).notempty()

    def discounted_price(self, discount_policy):
        """Return the discounted price for an item."""
        return Price.query.filter(
            Price.item == self, Price.discount_policy == discount_policy
        ).one_or_none()

    def standard_prices(self):
        return Price.query.filter(
            Price.item == self, Price.discount_policy_id.is_(None)
        ).order_by(Price.start_at.desc())

    def price_at(self, timestamp):
        """Return the price object for an item at a given time."""
        return (
            Price.query.filter(
                Price.item == self,
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
        Check if an item is available.

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
        """Return a query object preset with an item's confirmed line items."""
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
    def net_sales(self):
        return (
            db.session.query(sa.func.sum(LineItem.final_amount))
            .filter(
                LineItem.item == self, LineItem.status == LINE_ITEM_STATUS.CONFIRMED
            )
            .first()[0]
        )

    @classmethod
    def get_availability(cls, item_ids):
        """
        Return an availability dict.

        {'item_id': ('item title', 'quantity_total', 'line_item_count')}
        """
        items_dict = {}
        item_tups = (
            db.session.query(
                cls.id, cls.title, cls.quantity_total, sa.func.count(cls.id)
            )
            .join(LineItem)
            .filter(
                LineItem.item_id.in_(item_ids),
                LineItem.status == LINE_ITEM_STATUS.CONFIRMED,
            )
            .group_by(cls.id)
            .all()
        )
        for item_tup in item_tups:
            items_dict[str(item_tup[0])] = item_tup[1:]
        return items_dict

    def demand_curve(self):
        query = (
            db.session.query(sa.column('final_amount'), sa.column('count'))
            .from_statement(
                sa.text(
                    '''
            SELECT final_amount, count(*)
            FROM line_item
            WHERE item_id = :item_id
            AND final_amount > 0
            AND status = :status
            GROUP BY final_amount
            ORDER BY final_amount;
        '''
                )
            )
            .params(item_id=self.id, status=LINE_ITEM_STATUS.CONFIRMED)
        )
        return db.session.execute(query).fetchall()


class Price(BaseScopedNameMixin, Model):
    __tablename__ = 'price'
    __uuid_primary_key__ = True
    __table_args__ = (
        sa.UniqueConstraint('item_id', 'name'),
        sa.CheckConstraint('start_at < end_at', 'price_start_at_lt_end_at_check'),
        sa.UniqueConstraint('item_id', 'discount_policy_id'),
    )

    item_id: Mapped[UUID] = sa.orm.mapped_column(
        sa.ForeignKey('item.id'), nullable=False
    )
    item = relationship(Item, backref=backref('prices', cascade='all, delete-orphan'))

    discount_policy_id: Mapped[UUID] = sa.orm.mapped_column(
        sa.ForeignKey('discount_policy.id'), nullable=True
    )
    discount_policy = relationship(
        'DiscountPolicy', backref=backref('price', cascade='all, delete-orphan')
    )

    parent = sa.orm.synonym('item')
    start_at = sa.Column(
        sa.TIMESTAMP(timezone=True), default=sa.func.utcnow(), nullable=False
    )
    end_at = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False)

    amount = sa.Column(sa.Numeric, default=Decimal(0), nullable=False)
    currency = sa.Column(sa.Unicode(3), nullable=False, default='INR')

    __roles__ = {
        'price_owner': {
            'read': {
                'id',
                'item_id',
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
        if (
            self.item.item_collection.organization.userid
            in actor.organizations_owned_ids()
        ):
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
