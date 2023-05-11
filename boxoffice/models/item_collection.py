from __future__ import annotations

from . import BaseScopedNameMixin, Mapped, MarkdownColumn, db, sa
from .user import Organization
from .utils import HeadersAndDataTuple

__all__ = ['ItemCollection']


class ItemCollection(BaseScopedNameMixin, db.Model):  # type: ignore[name-defined]
    """Represent a collection of items or an inventory."""

    __tablename__ = 'item_collection'
    __uuid_primary_key__ = True
    __table_args__ = (sa.UniqueConstraint('organization_id', 'name'),)

    description = MarkdownColumn('description', default='', nullable=False)

    organization_id: Mapped[int] = sa.orm.mapped_column(
        sa.ForeignKey('organization.id'), nullable=False
    )
    organization = sa.orm.relationship(
        Organization,
        backref=sa.orm.backref('item_collections', cascade='all, delete-orphan'),
    )
    parent = sa.orm.synonym('organization')
    tax_type = sa.Column(sa.Unicode(80), nullable=True, default='GST')
    # ISO 3166-2 code. Eg: KA for Karnataka
    place_supply_state_code = sa.Column(sa.Unicode(3), nullable=True)
    # ISO country code
    place_supply_country_code = sa.Column(sa.Unicode(2), nullable=True)

    __roles__ = {'ic_owner': {'read': {'id', 'name', 'title', 'description'}}}

    def roles_for(self, actor=None, anchors=()):
        roles = super().roles_for(actor, anchors)
        if self.organization.userid in actor.organizations_owned_ids():
            roles.add('ic_owner')
        return roles

    def fetch_all_details(self):
        """
        Return details for all line items in a given item collection.

        Also return the associated assignee (if any), discount policy (if any),
        discount coupon (if any), item, order and order session (if any)
        as a tuple of (keys, rows).
        """
        line_item_join = (
            sa.outerjoin(
                LineItem,
                Assignee,
                sa.and_(
                    LineItem.id == Assignee.line_item_id, Assignee.current.is_(True)
                ),
            )
            .outerjoin(DiscountCoupon, LineItem.discount_coupon_id == DiscountCoupon.id)
            .outerjoin(DiscountPolicy, LineItem.discount_policy_id == DiscountPolicy.id)
            .join(Item)
            .join(Order)
            .outerjoin(OrderSession)
        )

        line_item_query = (
            sa.select(
                LineItem.id,
                LineItem.customer_order_id,
                Order.invoice_no,
                Item.title,
                LineItem.base_amount,
                LineItem.discounted_amount,
                LineItem.final_amount,
                DiscountPolicy.title,
                DiscountCoupon.code,
                Order.buyer_fullname,
                Order.buyer_email,
                Order.buyer_phone,
                Assignee.fullname,
                Assignee.email,
                Assignee.phone,
                Order.access_token,
                Assignee.details,
                OrderSession.utm_campaign,
                OrderSession.utm_source,
                OrderSession.utm_medium,
                OrderSession.utm_term,
                OrderSession.utm_content,
                OrderSession.utm_id,
                OrderSession.gclid,
                OrderSession.referrer,
                OrderSession.host,
                Order.paid_at,
            )
            .select_from(line_item_join)
            .where(LineItem.status == LINE_ITEM_STATUS.CONFIRMED)
            .where(Order.item_collection == self)
            .order_by(LineItem.ordered_at)
        )
        # TODO: Use label() instead of this hack https://github.com/hasgeek/boxoffice/pull/236#discussion_r223341927
        return HeadersAndDataTuple(
            [
                'ticket_id',
                'order_id',
                'receipt_no',
                'ticket_type',
                'base_amount',
                'discounted_amount',
                'final_amount',
                'discount_policy',
                'discount_code',
                'buyer_fullname',
                'buyer_email',
                'buyer_phone',
                'attendee_fullname',
                'attendee_email',
                'attendee_phone',
                'assignee_url',
                'attendee_details',
                'utm_campaign',
                'utm_source',
                'utm_medium',
                'utm_term',
                'utm_content',
                'utm_id',
                'gclid',
                'referrer',
                'host',
                'date',
            ],
            db.session.execute(line_item_query).fetchall(),
        )

    def fetch_assignee_details(self):
        """
        Return assignee details for all items in the item collection.

        Includes invoice_no, ticket title, assignee fullname, assignee email, assignee
        phone and assignee details for all the line items in a given item collection
        as a tuple of (keys, rows).
        """
        line_item_join = (
            sa.join(
                LineItem,
                Assignee,
                sa.and_(
                    LineItem.id == Assignee.line_item_id, Assignee.current.is_(True)
                ),
            )
            .join(Item)
            .join(Order)
        )
        line_item_query = (
            sa.select(
                Order.invoice_no,
                LineItem.line_item_seq,
                LineItem.id,
                Item.title,
                Assignee.fullname,
                Assignee.email,
                Assignee.phone,
                Assignee.details,
            )
            .select_from(line_item_join)
            .where(LineItem.status == LINE_ITEM_STATUS.CONFIRMED)
            .where(Order.item_collection == self)
            .order_by(LineItem.ordered_at)
        )
        return HeadersAndDataTuple(
            [
                'receipt_no',
                'ticket_no',
                'ticket_id',
                'ticket_type',
                'attendee_fullname',
                'attendee_email',
                'attendee_phone',
                'attendee_details',
            ],
            db.session.execute(line_item_query).fetchall(),
        )


# Tail imports
from .discount_policy import DiscountCoupon, DiscountPolicy  # isort:skip
from .line_item import LINE_ITEM_STATUS, Assignee, LineItem  # isort:skip
from .item import Item  # isort:skip
from .order import Order, OrderSession  # isort:skip
