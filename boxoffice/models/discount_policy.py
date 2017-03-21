# -*- coding: utf-8 -*-

import string
import random
from datetime import datetime
from werkzeug import cached_property
from itsdangerous import Signer, BadSignature
from sqlalchemy import event
from baseframe import __
from coaster.utils import LabeledEnum, uuid1mc, buid
from boxoffice.models import db, IdMixin, BaseScopedNameMixin
from boxoffice.models import Organization

__all__ = ['DiscountPolicy', 'DiscountCoupon', 'item_discount_policy', 'DISCOUNT_TYPE']


class DISCOUNT_TYPE(LabeledEnum):
    AUTOMATIC = (0, __("Automatic"))
    COUPON = (1, __("Coupon"))


item_discount_policy = db.Table('item_discount_policy', db.Model.metadata,
    db.Column('item_id', None, db.ForeignKey('item.id'), primary_key=True),
    db.Column('discount_policy_id', None, db.ForeignKey('discount_policy.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow, nullable=False))


class DiscountPolicy(BaseScopedNameMixin, db.Model):
    """
    Consists of the discount rules applicable on items

    `title` has a GIN index to enable trigram matching.
    """
    __tablename__ = 'discount_policy'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('organization_id', 'name'),
        db.UniqueConstraint('organization_id', 'discount_code_base'),
        db.CheckConstraint('percentage > 0 and percentage <= 100', 'discount_policy_percentage_check'),
        db.CheckConstraint('discount_type = 0 or (discount_type = 1 and bulk_coupon_usage_limit IS NOT NULL)', 'discount_policy_bulk_coupon_usage_limit_check'))

    organization_id = db.Column(None, db.ForeignKey('organization.id'), nullable=False)
    organization = db.relationship(Organization, backref=db.backref('discount_policies', order_by='DiscountPolicy.created_at.desc()', lazy='dynamic', cascade='all, delete-orphan'))
    parent = db.synonym('organization')

    discount_type = db.Column(db.Integer, default=DISCOUNT_TYPE.AUTOMATIC, nullable=False)

    # Minimum number of a particular item that needs to be bought for this discount to apply
    item_quantity_min = db.Column(db.Integer, default=1, nullable=False)
    percentage = db.Column(db.Integer, nullable=True)
    # price-based discount
    is_price_based = db.Column(db.Boolean, default=False, nullable=False)

    discount_code_base = db.Column(db.Unicode(20), nullable=True)
    secret = db.Column(db.Unicode(50), nullable=True)

    items = db.relationship('Item', secondary=item_discount_policy)
    # Coupons generated in bulk are not stored in the database during generation.
    # This field allows specifying the number of times a coupon, generated in bulk, can be used
    # This is particularly useful for generating referral discount coupons. For instance, one could generate
    # a signed coupon and provide it to a user such that the user can share the coupon `n` times
    # `n` here is essentially bulk_coupon_usage_limit.
    bulk_coupon_usage_limit = db.Column(db.Integer, nullable=True, default=1)

    @cached_property
    def is_automatic(self):
        return self.discount_type == DISCOUNT_TYPE.AUTOMATIC

    @cached_property
    def is_coupon(self):
        return self.discount_type == DISCOUNT_TYPE.COUPON

    def gen_signed_code(self, identifier=None):
        """Generates a signed code in the format discount_code_base.randint.signature"""
        if not identifier:
            identifier = buid()
        signer = Signer(self.secret)
        key = "{base}.{identifier}".format(base=self.discount_code_base, identifier=identifier)
        return signer.sign(key)

    @staticmethod
    def is_signed_code_format(code):
        """Checks if the code is in the {x.y.z} format"""
        return len(code.split('.')) == 3 if code else False

    @classmethod
    def get_from_signed_code(cls, code):
        """Returns a discount policy given a valid signed code, returns None otherwise"""
        if not cls.is_signed_code_format(code):
            return None
        discount_code_base = code.split('.')[0]
        policy = cls.query.filter_by(discount_code_base=discount_code_base).one_or_none()
        if not policy:
            return None
        signer = Signer(policy.secret)
        try:
            signer.unsign(code)
            return policy
        except BadSignature:
            return None

    def set_secret(self, secret=None):
        """Sets a given value or buid as the secret for the discount policy object"""
        self.secret = secret if secret else buid()
        return self.secret

    @classmethod
    def make_bulk(cls, discount_code_base, **kwargs):
        """
        Returns a discount policy for the purpose of issuing signed discount coupons in bulk.
        """
        return cls(discount_type=DISCOUNT_TYPE.COUPON, discount_code_base=discount_code_base, secret=buid(), **kwargs)


@event.listens_for(DiscountPolicy, 'before_update')
@event.listens_for(DiscountPolicy, 'before_insert')
def validate_price_based_discount(mapper, connection, target):
    if target.is_price_based and len(target.items) > 1:
        raise ValueError("Price-based discounts MUST have only one associated item")


def generate_coupon_code(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class DiscountCoupon(IdMixin, db.Model):
    __tablename__ = 'discount_coupon'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('discount_policy_id', 'code'),)

    def __init__(self, *args, **kwargs):
        self.id = uuid1mc()
        super(DiscountCoupon, self).__init__(*args, **kwargs)

    code = db.Column(db.Unicode(100), nullable=False, default=generate_coupon_code)
    usage_limit = db.Column(db.Integer, nullable=False, default=1)
    used_count = db.Column(db.Integer, nullable=False, default=0)

    discount_policy_id = db.Column(None, db.ForeignKey('discount_policy.id'), nullable=False)
    discount_policy = db.relationship(DiscountPolicy, backref=db.backref('discount_coupons', cascade='all, delete-orphan'))
