"""Discount policy model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, List, Optional, Sequence
from uuid import UUID
import secrets
import string

from itsdangerous import BadSignature, Signer
from sqlalchemy.orm.exc import MultipleResultsFound
from werkzeug.utils import cached_property

from coaster.sqlalchemy import LazyRoleSet
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


class DiscountPolicy(BaseScopedNameMixin, Model):
    """
    Consists of the discount rules applicable on tickets.

    `title` has a GIN index to enable trigram matching.
    """

    __tablename__ = 'discount_policy'
    __uuid_primary_key__ = True
    __table_args__ = (
        sa.UniqueConstraint('organization_id', 'name'),
        sa.UniqueConstraint('organization_id', 'discount_code_base'),
        sa.CheckConstraint(
            'percentage > 0 and percentage <= 100', 'discount_policy_percentage_check'
        ),
        sa.CheckConstraint(
            'discount_type = 0 or'
            ' (discount_type = 1 and bulk_coupon_usage_limit IS NOT NULL)',
            'discount_policy_bulk_coupon_usage_limit_check',
        ),
    )

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
    percentage: Mapped[Optional[int]]
    # price-based discount
    is_price_based: Mapped[bool] = sa.orm.mapped_column(default=False)

    discount_code_base: Mapped[Optional[str]] = sa.orm.mapped_column(sa.Unicode(20))
    secret: Mapped[Optional[str]] = sa.orm.mapped_column(sa.Unicode(50))

    # Coupons generated in bulk are not stored in the database during generation. This
    # field allows specifying the number of times a coupon, generated in bulk, can be
    # used This is particularly useful for generating referral discount coupons. For
    # instance, one could generate a signed coupon and provide it to a user such that
    # the user can share the coupon `n` times `n` here is essentially
    # bulk_coupon_usage_limit.
    bulk_coupon_usage_limit: Mapped[Optional[int]] = sa.orm.mapped_column(default=1)

    discount_coupons: Mapped[List[DiscountCoupon]] = relationship(
        cascade='all, delete-orphan', back_populates='discount_policy'
    )
    tickets: Mapped[List[Item]] = relationship(
        secondary=item_discount_policy, back_populates='discount_policies'
    )
    prices: Mapped[List[Price]] = relationship(cascade='all, delete-orphan')
    line_items: DynamicMapped[LineItem] = relationship(
        lazy='dynamic', back_populates='discount_policy'
    )

    __roles__ = {
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

    def roles_for(
        self, actor: Optional[User] = None, anchors: Sequence[Any] = ()
    ) -> LazyRoleSet:
        roles = super().roles_for(actor, anchors)
        if (
            actor is not None
            and self.organization.userid in actor.organizations_owned_ids()
        ):
            roles.add('dp_owner')
        return roles

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

    def gen_signed_code(self, identifier: Optional[str] = None) -> str:
        """
        Generate a signed code.

        Format: ``discount_code_base.randint.signature``
        """
        if not self.secret:
            raise TypeError("DiscountPolicy.secret is unset")
        if not identifier:
            identifier = secrets.token_urlsafe(16)
        signer = Signer(self.secret)
        key = f'{self.discount_code_base}.{identifier}'
        return signer.sign(key).decode('utf-8')

    @staticmethod
    def is_signed_code_format(code) -> bool:
        """Check if the code is in the {x.y.z} format."""
        return len(code.split('.')) == 3 if code else False

    @classmethod
    def get_from_signed_code(cls, code, organization_id) -> Optional[DiscountPolicy]:
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
    def make_bulk(cls, discount_code_base, **kwargs) -> DiscountPolicy:
        """Return a discount policy for bulk discount coupons."""
        return cls(
            discount_type=DiscountTypeEnum.COUPON,
            discount_code_base=discount_code_base,
            secret=buid(),
            **kwargs,
        )

    @classmethod
    def get_from_ticket(
        cls, ticket: Item, qty, coupon_codes: Sequence[str] = ()
    ) -> List[PolicyCoupon]:
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
    def line_items_count(self):
        return self.line_items.filter(
            LineItem.status == LineItemStatus.CONFIRMED
        ).count()

    @classmethod
    def is_valid_access_coupon(cls, ticket: Item, code_list):
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
def validate_price_based_discount(mapper, connection, target: DiscountPolicy):
    if target.is_price_based and len(target.tickets) > 1:
        raise ValueError("Price-based discounts MUST have only one associated ticket")


def generate_coupon_code(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(secrets.choice(chars) for _ in range(size))


class DiscountCoupon(IdMixin, Model):
    __tablename__ = 'discount_coupon'
    __uuid_primary_key__ = True
    __table_args__ = (sa.UniqueConstraint('discount_policy_id', 'code'),)

    def __init__(self, *args, **kwargs):
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
    line_items: Mapped[List[LineItem]] = relationship(back_populates='discount_coupon')

    @classmethod
    def is_signed_code_usable(cls, policy, code):
        obj = cls.query.filter(
            cls.discount_policy == policy,
            cls.code == code,
            cls.used_count == cls.usage_limit,
        ).one_or_none()
        if obj:
            return False
        return True

    def update_used_count(self):
        self.used_count = (
            sa.select(sa.func.count())
            .where(LineItem.discount_coupon == self)
            .where(LineItem.status == LineItemStatus.CONFIRMED)
            .as_scalar()
        )


@dataclass
class PolicyCoupon:
    policy: DiscountPolicy
    coupon: Optional[DiscountCoupon]


create_title_trgm_trigger = sa.DDL(
    'CREATE INDEX idx_discount_policy_title_trgm on discount_policy'
    ' USING gin (title gin_trgm_ops);'
)

sa.event.listen(
    DiscountPolicy.__table__,
    'after_create',
    create_title_trgm_trigger.execute_if(dialect='postgresql'),
)

# Tail imports
from .line_item import LineItem  # isort:skip

if TYPE_CHECKING:
    from .item import Item, Price
    from .user import Organization, User
