"""Discount policy model."""

from __future__ import annotations

import secrets
import string
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Self
from uuid import UUID

from itsdangerous import BadSignature, Signer
from sqlalchemy.orm.exc import MultipleResultsFound
from werkzeug.utils import cached_property

from coaster.sqlalchemy import role_check
from coaster.utils import buid, uuid1mc

from . import (
    BaseScopedNameMixin,
    DynamicMapped,
    IdMixin,
    Mapped,
    Model,
    db,
    relationship,
    sa,
)
from .enums import DiscountTypeEnum, LineItemStatus
from .user import Organization, User

__all__ = ['DiscountPolicy', 'DiscountCoupon', 'item_discount_policy']


item_discount_policy = sa.Table(
    'item_discount_policy',
    Model.metadata,
    sa.Column('item_id', sa.ForeignKey('item.id'), primary_key=True),
    sa.Column(
        'discount_policy_id',
        sa.ForeignKey('discount_policy.id'),
        primary_key=True,
    ),
    sa.Column(
        'created_at',
        sa.TIMESTAMP(timezone=True),
        default=sa.func.utcnow(),
        nullable=False,
    ),
)


class DiscountPolicy(BaseScopedNameMixin[UUID, User], Model):
    """
    Consists of the discount rules applicable on tickets.

    `title` has a GIN index to enable trigram matching.
    """

    __tablename__ = 'discount_policy'
    organization_id: Mapped[int] = sa.orm.mapped_column(
        sa.ForeignKey('organization.id')
    )
    organization: Mapped[Organization] = relationship(
        back_populates='discount_policies'
    )
    parent: Mapped[Organization] = sa.orm.synonym('organization')

    discount_type: Mapped[int] = sa.orm.mapped_column(
        default=DiscountTypeEnum.AUTOMATIC
    )

    # Minimum number of a particular ticket that needs to be bought for this discount to
    # apply
    item_quantity_min: Mapped[int] = sa.orm.mapped_column(default=1)

    # TODO: Add check constraint requiring percentage if is_price_based is false
    percentage: Mapped[int | None] = sa.orm.mapped_column()
    # price-based discount
    is_price_based: Mapped[bool] = sa.orm.mapped_column(default=False)

    discount_code_base: Mapped[str | None] = sa.orm.mapped_column(sa.Unicode(20))
    secret: Mapped[str | None] = sa.orm.mapped_column(sa.Unicode(50))

    # Coupons generated in bulk are not stored in the database during generation. This
    # field allows specifying the number of times a coupon, generated in bulk, can be
    # used This is particularly useful for generating referral discount coupons. For
    # instance, one could generate a signed coupon and provide it to a user such that
    # the user can share the coupon `n` times `n` here is essentially
    # bulk_coupon_usage_limit.
    bulk_coupon_usage_limit: Mapped[int | None] = sa.orm.mapped_column(default=1)

    discount_coupons: Mapped[list[DiscountCoupon]] = relationship(
        cascade='all, delete-orphan', back_populates='discount_policy'
    )
    tickets: Mapped[list[Ticket]] = relationship(
        secondary=item_discount_policy, back_populates='discount_policies'
    )
    prices: Mapped[list[Price]] = relationship(cascade='all, delete-orphan')
    line_items: DynamicMapped[LineItem] = relationship(
        lazy='dynamic', back_populates='discount_policy'
    )

    __table_args__ = (
        sa.UniqueConstraint(organization_id, 'name'),
        sa.UniqueConstraint(organization_id, discount_code_base),
        sa.CheckConstraint(
            sa.or_(
                sa.and_(is_price_based.is_(True), percentage.is_(None)),
                sa.and_(
                    is_price_based.is_(False),
                    percentage.isnot(None),
                    percentage > 0,
                    percentage <= 100,
                ),
            ),
            'discount_policy_percentage_check',
        ),
        sa.CheckConstraint(
            sa.or_(
                discount_type == int(DiscountTypeEnum.AUTOMATIC),
                sa.and_(
                    discount_type == int(DiscountTypeEnum.COUPON),
                    bulk_coupon_usage_limit.isnot(None),
                ),
            ),
            'discount_policy_bulk_coupon_usage_limit_check',
        ),
        sa.Index(
            'idx_discount_policy_title_trgm',
            'title',
            postgresql_using='gin',
            postgresql_ops={'title': 'gin_trgm_ops'},
        ),
    )

    __roles__: ClassVar = {
        'dp_owner': {
            'read': {
                'id',
                'name',
                'title',
                'is_automatic',
                'is_coupon',
                'item_quantity_min',
                'percentage',
                'is_price_based',
                'discount_code_base',
                'bulk_coupon_usage_limit',
                'line_items_count',
            }
        }
    }

    @role_check('dp_owner')
    def has_dp_owner_role(self, actor: User | None, _anchors: Any = ()) -> bool:
        return (
            actor is not None
            and self.organization.userid in actor.organizations_owned_ids()
        )

    def __init__(self, *args, **kwargs) -> None:
        secret = kwargs.pop('secret', None)
        super().__init__(*args, **kwargs)
        self.secret = secret or secrets.token_urlsafe(16)

    @cached_property
    def is_automatic(self) -> bool:
        return self.discount_type == DiscountTypeEnum.AUTOMATIC

    @cached_property
    def is_coupon(self) -> bool:
        return self.discount_type == DiscountTypeEnum.COUPON

    def gen_signed_code(self, identifier: str | None = None) -> str:
        """
        Generate a signed code.

        Format: ``discount_code_base.randint.signature``
        """
        if not self.secret:
            msg = "DiscountPolicy.secret is unset"
            raise TypeError(msg)
        if not identifier:
            identifier = secrets.token_urlsafe(16)
        signer = Signer(self.secret)
        key = f'{self.discount_code_base}.{identifier}'
        return signer.sign(key).decode('utf-8')

    @staticmethod
    def is_signed_code_format(code: str) -> bool:
        """Check if the code is in the {x.y.z} format."""
        return len(code.split('.')) == 3 if code else False

    @classmethod
    def get_from_signed_code(
        cls, code: str, organization_id: int
    ) -> DiscountPolicy | None:
        """Return a discount policy given a valid signed code, None otherwise."""
        if not cls.is_signed_code_format(code):
            return None
        discount_code_base = code.split('.')[0]
        policy = cls.query.filter_by(
            discount_code_base=discount_code_base, organization_id=organization_id
        ).one_or_none()
        if not policy or not policy.secret:
            return None
        signer = Signer(policy.secret)
        try:
            signer.unsign(code)
            return policy
        except BadSignature:
            return None

    @classmethod
    def make_bulk(cls, discount_code_base: str | None, **kwargs) -> Self:
        """Return a discount policy for bulk discount coupons."""
        return cls(
            discount_type=DiscountTypeEnum.COUPON,
            discount_code_base=discount_code_base,
            secret=buid(),
            **kwargs,
        )

    @classmethod
    def get_from_ticket(
        cls, ticket: Ticket, qty: int, coupon_codes: Sequence[str] = ()
    ) -> list[PolicyCoupon]:
        """
        Return a list of (discount_policy, discount_coupon) tuples.

        Applicable for a ticket, given the quantity of line items and coupons if any.
        """
        automatic_discounts = ticket.discount_policies.filter(
            cls.discount_type == DiscountTypeEnum.AUTOMATIC,
            cls.item_quantity_min <= qty,
        ).all()
        policies = [PolicyCoupon(discount, None) for discount in automatic_discounts]
        if not coupon_codes:
            return policies
        coupon_policies = ticket.discount_policies.filter(
            cls.discount_type == DiscountTypeEnum.COUPON
        ).all()
        coupon_policy_ids = [cp.id for cp in coupon_policies]
        for coupon_code in coupon_codes:
            coupons = []
            if cls.is_signed_code_format(coupon_code):
                policy = cls.get_from_signed_code(
                    coupon_code, ticket.menu.organization_id
                )
                if policy and policy.id in coupon_policy_ids:
                    coupon = DiscountCoupon.query.filter_by(
                        discount_policy=policy, code=coupon_code
                    ).one_or_none()
                    if not coupon:
                        coupon = DiscountCoupon(
                            discount_policy=policy,
                            code=coupon_code,
                            usage_limit=policy.bulk_coupon_usage_limit,
                            used_count=0,
                        )
                        db.session.add(coupon)
                    coupons.append(coupon)
            else:
                coupons = DiscountCoupon.query.filter(
                    DiscountCoupon.discount_policy_id.in_(coupon_policy_ids),
                    DiscountCoupon.code == coupon_code,
                ).all()

            for coupon in coupons:
                if coupon.usage_limit > coupon.used_count:
                    policies.append(PolicyCoupon(coupon.discount_policy, coupon))
        return policies

    @property
    def line_items_count(self) -> int:
        return self.line_items.filter(
            LineItem.status == LineItemStatus.CONFIRMED
        ).count()

    @classmethod
    def is_valid_access_coupon(cls, ticket: Ticket, code_list: list[str]) -> bool:
        """
        Check if any of code_list is a valid access code for the specified ticket.

        A supplied coupon code can be either a signed coupon code or a custom code.
        Both cases are checked for. Used signed coupon codes are stored and rejected for
        reuse.
        """
        for code in code_list:
            if cls.is_signed_code_format(code):
                policy = cls.get_from_signed_code(code, ticket.menu.organization_id)
                if policy and not DiscountCoupon.is_signed_code_usable(policy, code):
                    break
            else:
                try:
                    policy = (
                        cls.query.join(
                            DiscountCoupon,
                            DiscountCoupon.discount_policy_id == DiscountPolicy.id,
                        )
                        .filter(
                            DiscountCoupon.code == code,
                            DiscountCoupon.used_count < DiscountCoupon.usage_limit,
                        )
                        .one_or_none()
                    )
                except MultipleResultsFound:
                    # ref: https://github.com/hasgeek/boxoffice/issues/290
                    policy = None
            if policy is not None and policy in ticket.discount_policies:
                return True
        return False


@sa.event.listens_for(DiscountPolicy, 'before_update')
@sa.event.listens_for(DiscountPolicy, 'before_insert')
def validate_price_based_discount(
    _mapper: Any, _connection: Any, target: DiscountPolicy
) -> None:
    if target.is_price_based and len(target.tickets) > 1:
        msg = "Price-based discounts MUST have only one associated ticket"
        raise ValueError(msg)


def generate_coupon_code(
    size: int = 6, chars: str = string.ascii_uppercase + string.digits
) -> str:
    return ''.join(secrets.choice(chars) for _ in range(size))


class DiscountCoupon(IdMixin[UUID], Model):
    __tablename__ = 'discount_coupon'

    def __init__(self, *args, **kwargs) -> None:
        self.id = uuid1mc()
        super().__init__(*args, **kwargs)

    code: Mapped[str] = sa.orm.mapped_column(
        sa.Unicode(100), default=generate_coupon_code
    )
    usage_limit: Mapped[int] = sa.orm.mapped_column(default=1)
    used_count: Mapped[int] = sa.orm.mapped_column(default=0)

    discount_policy_id: Mapped[UUID] = sa.orm.mapped_column(
        sa.ForeignKey('discount_policy.id')
    )
    discount_policy: Mapped[DiscountPolicy] = relationship(
        back_populates='discount_coupons'
    )
    line_items: Mapped[list[LineItem]] = relationship(back_populates='discount_coupon')

    __table_args__ = (sa.UniqueConstraint(discount_policy_id, code),)

    @classmethod
    def is_signed_code_usable(cls, policy: DiscountPolicy, code: str) -> bool:
        obj = cls.query.filter(
            cls.discount_policy == policy,
            cls.code == code,
            cls.used_count == cls.usage_limit,
        ).one_or_none()
        if obj:
            return False
        return True

    def update_used_count(self) -> None:
        self.used_count = (
            sa.select(sa.func.count())
            .where(LineItem.discount_coupon_id == self.id)
            .where(LineItem.status == LineItemStatus.CONFIRMED)
            .as_scalar()
        )


@dataclass
class PolicyCoupon:
    policy: DiscountPolicy
    coupon: DiscountCoupon | None


# Tail imports
from .line_item import LineItem  # isort:skip

if TYPE_CHECKING:
    from .ticket import Price, Ticket
