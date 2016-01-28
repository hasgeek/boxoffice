from boxoffice.models import db, BaseNameMixin, IdMixin
from datetime import datetime
from baseframe import __
from coaster.utils import LabeledEnum

import string
import random

__all__ = ['DiscountPolicy', 'DiscountCoupon', 'item_discount_policy']


def generate_coupon_code(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class DISCOUNTTYPES(LabeledEnum):
    AUTOMATIC = (0, __("Automatic"))
    COUPON = (1, __("Coupon"))


item_discount_policy = db.Table('item_discount_policy', db.Model.metadata,
    db.Column('item_id', None, db.ForeignKey('item.id'), primary_key=True),
    db.Column('discount_policy_id', None, db.ForeignKey('discount_policy.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow, nullable=False)
    )


class DiscountPolicy(BaseNameMixin, db.Model):
    """
    DiscountPolicy are rules for prices applied on items at the time of purchase
    """
    __tablename__ = 'discount_policy'
    __uuid_primary_key__ = True

    discount_type = db.Column(db.Integer, default=DISCOUNTTYPES.AUTOMATIC, nullable=False)

    quantity_from = db.Column(db.Integer, default=1, nullable=False)
    quantity_to = db.Column(db.Integer, nullable=True)

    percentage = db.Column(db.Integer, nullable=False)

    items = db.relationship('Item', secondary=item_discount_policy)

    __table_args__ = (db.CheckConstraint('percentage <= 100', 'percentage_bound_upper'), db.CheckConstraint('percentage > 0', 'percentage_bound_lower'))
    # add check constraint quantity_from <= quantity_to



class DiscountCoupon(IdMixin, db.Model):
    __tablename__ = 'discount_coupon'
    code = db.Column(db.Unicode(6), default=generate_coupon_code, nullable=False)

    discount_policy_id = db.Column(None, db.ForeignKey('discount_policy.id'), nullable=False)
    discount_policy = db.relationship(DiscountPolicy,
        backref=db.backref('discount_coupons', cascade='all, delete-orphan'))

    quantity_available = db.Column(db.Integer, default=0, nullable=False)
    quantity_total = db.Column(db.Integer, default=0, nullable=False)

    __table_args__ = (db.UniqueConstraint('code', 'discount_policy_id'),)
    # add check constraint quantity_available <= quantity_total
