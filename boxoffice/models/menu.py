from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Any, ClassVar, cast
from uuid import UUID

from sqlalchemy.ext.orderinglist import ordering_list

from coaster.sqlalchemy import role_check

from . import (
    BaseScopedNameMixin,
    DynamicMapped,
    Mapped,
    MarkdownColumn,
    Model,
    db,
    relationship,
    sa,
)
from .enums import LineItemStatus, TransactionTypeEnum
from .payment import PaymentTransaction
from .user import Organization, User
from .utils import HeadersAndDataTuple

__all__ = ['Menu']


class Menu(BaseScopedNameMixin[UUID, User], Model):
    """Represent a collection of tickets."""

    __tablename__ = 'item_collection'
    __table_args__ = (sa.UniqueConstraint('organization_id', 'name'),)

    description = MarkdownColumn('description', default='', nullable=False)

    organization_id: Mapped[int] = sa.orm.mapped_column(
        sa.ForeignKey('organization.id')
    )
    organization: Mapped[Organization] = relationship(back_populates='menus')
    parent: Mapped[Organization] = sa.orm.synonym('organization')
    tax_type: Mapped[str | None] = sa.orm.mapped_column(sa.Unicode(80), default='GST')
    # ISO 3166-2 code. Eg: KA for Karnataka
    place_supply_state_code: Mapped[str | None] = sa.orm.mapped_column(sa.Unicode(3))
    # ISO country code
    place_supply_country_code: Mapped[str | None] = sa.orm.mapped_column(sa.Unicode(2))

    categories: Mapped[list[Category]] = relationship(
        cascade='all, delete-orphan',
        order_by='Category.seq',
        collection_class=ordering_list('seq', count_from=1),
        back_populates='menu',
    )
    tickets: Mapped[list[Ticket]] = relationship(
        cascade='all, delete-orphan',
        order_by=lambda: Ticket.seq,
        collection_class=ordering_list('seq', count_from=1),
        back_populates='menu',
    )
    orders: DynamicMapped[Order] = relationship(
        cascade='all, delete-orphan', lazy='dynamic', back_populates='menu'
    )

    __roles__: ClassVar = {'ic_owner': {'read': {'id', 'name', 'title', 'description'}}}

    @role_check('ic_owner')
    def has_ic_owner_role(self, actor: User | None, _anchors: Any = ()) -> bool:
        return (
            actor is not None
            and self.organization.userid in actor.organizations_owned_ids()
        )

    def fetch_all_details(self) -> HeadersAndDataTuple:
        """
        Return details for all order lineitems in a given menu.

        Also return the associated assignee (if any), discount policy (if any),
        discount coupon (if any), ticket, order and order session (if any)
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
            .join(Ticket)
            .join(Order)
            .outerjoin(OrderSession)
        )

        line_item_query = (
            sa.select(
                LineItem.id,
                LineItem.customer_order_id,
                Order.receipt_no,
                Ticket.title,
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
            .where(LineItem.status == LineItemStatus.CONFIRMED)
            .where(Order.menu_id == self.id)
            .order_by(LineItem.ordered_at)
        )
        # TODO: Use label() instead of this hack
        # https://github.com/hasgeek/boxoffice/pull/236#discussion_r223341927
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

    def fetch_assignee_details(self) -> HeadersAndDataTuple:
        """
        Return assignee details for all ordered tickets in the menu.

        Includes receipt_no, ticket title, assignee fullname, assignee email, assignee
        phone and assignee details for all the ordered line items in a given menu as a
        tuple of (keys, rows).
        """
        line_item_join = (
            sa.join(
                LineItem,
                Assignee,
                sa.and_(
                    LineItem.id == Assignee.line_item_id, Assignee.current.is_(True)
                ),
            )
            .join(Ticket)
            .join(Order)
        )
        line_item_query = (
            sa.select(
                Order.receipt_no,
                LineItem.line_item_seq,
                LineItem.id,
                Ticket.title,
                Assignee.fullname,
                Assignee.email,
                Assignee.phone,
                Assignee.details,
            )
            .select_from(line_item_join)
            .where(LineItem.status == LineItemStatus.CONFIRMED)
            .where(Order.menu_id == self.id)
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

    def net_sales(self) -> Decimal:
        """Return the net revenue for a menu."""
        total_paid = cast(
            Decimal,
            db.session.scalar(
                sa.select(sa.func.sum(PaymentTransaction.amount))
                .select_from(PaymentTransaction)
                .join(Order, PaymentTransaction.customer_order_id == Order.id)
                .where(
                    PaymentTransaction.transaction_type == TransactionTypeEnum.PAYMENT,
                    Order.menu_id == self.id,
                )
            ),
        )
        total_refunded = cast(
            Decimal,
            db.session.scalar(
                sa.select(sa.func.sum(PaymentTransaction.amount))
                .select_from(PaymentTransaction)
                .join(Order, PaymentTransaction.customer_order_id == Order.id)
                .where(
                    PaymentTransaction.transaction_type == TransactionTypeEnum.REFUND,
                    Order.menu_id == self.id,
                )
            ),
        )

        if total_paid and total_refunded:
            return total_paid - total_refunded
        if total_paid:
            return total_paid
        return Decimal('0')


# Tail imports
from .discount_policy import DiscountCoupon, DiscountPolicy  # isort:skip
from .line_item import Assignee, LineItem  # isort:skip
from .ticket import Ticket  # isort:skip
from .order import Order, OrderSession  # isort:skip

if TYPE_CHECKING:
    from .category import Category
