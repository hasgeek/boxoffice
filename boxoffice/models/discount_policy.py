# -*- coding: utf-8 -*-

import string
import random
from datetime import datetime
from werkzeug import cached_property
from itsdangerous import Signer, BadSignature
from baseframe import __
from coaster.utils import LabeledEnum
from boxoffice.models import db, IdMixin, BaseScopedNameMixin
from boxoffice.models import Organization
from boxoffice import app

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
    """
    __tablename__ = 'discount_policy'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('organization_id', 'name'),
        db.UniqueConstraint('discount_code_base'),
        db.CheckConstraint('percentage > 0 and percentage <= 100', 'discount_policy_percentage_check'))

    organization_id = db.Column(None, db.ForeignKey('organization.id'), nullable=False)
    organization = db.relationship(Organization, backref=db.backref('discount_policies', cascade='all, delete-orphan'))
    parent = db.synonym('organization')

    discount_type = db.Column(db.Integer, default=DISCOUNT_TYPE.AUTOMATIC, nullable=False)

    # Minimum number of a particular item that needs to be bought for this discount to apply
    item_quantity_min = db.Column(db.Integer, default=1, nullable=False)
    percentage = db.Column(db.Integer, nullable=True)
    # price-based discount
    is_price_based = db.Column(db.Boolean, default=False, nullable=False)
    discount_code_base = db.Column(db.Unicode(20), nullable=True)

    items = db.relationship('Item', secondary=item_discount_policy)

    @cached_property
    def is_automatic(self):
        return self.discount_type == DISCOUNT_TYPE.AUTOMATIC

    @cached_property
    def is_coupon(self):
        return self.discount_type == DISCOUNT_TYPE.COUPON

    def gen_signed_code(self):
        """Generates a signed code in the format discount_code_base.randint.signature"""
        signer = Signer(app.config['SECRET_KEY'])
        key = "{base}.{randint}".format(base=self.discount_code_base, randint=random.randint(1, 10000))
        return signer.sign(key)

    @classmethod
    def get_from_signed_code(cls, code):
        """Returns a discount policy from a signed code"""
        signer = Signer(app.config['SECRET_KEY'])
        try:
            key = signer.unsign(code)
        except BadSignature:
            return None
        discount_code_base = key.split('.')[0]
        return cls.query.filter_by(discount_code_base=discount_code_base).one_or_none()


def generate_coupon_code(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class DiscountCoupon(IdMixin, db.Model):
    __tablename__ = 'discount_coupon'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('discount_policy_id', 'code'),)

    code = db.Column(db.Unicode(50), nullable=False, default=generate_coupon_code)
    usage_limit = db.Column(db.Integer, nullable=False, default=1)
    used_count = db.Column(db.Integer, nullable=False, default=0)

    discount_policy_id = db.Column(None, db.ForeignKey('discount_policy.id'), nullable=False)
    discount_policy = db.relationship(DiscountPolicy, backref=db.backref('discount_coupons', cascade='all, delete-orphan'))
