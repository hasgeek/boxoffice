import string
import random
from datetime import datetime
from baseframe import __
from coaster.utils import LabeledEnum
from boxoffice import app
from boxoffice.models import db, BaseScopedNameMixin, IdMixin
from boxoffice.models import Organization
from itsdangerous import Signer
from sqlalchemy import or_, and_

__all__ = ['DiscountPolicy', 'DiscountCoupon', 'item_discount_policy', 'DISCOUNT_TYPES']


class DISCOUNT_TYPES(LabeledEnum):
    AUTOMATIC = (0, __("Automatic"))
    COUPON = (1, __("Coupon"))


item_discount_policy = db.Table('item_discount_policy', db.Model.metadata,
    db.Column('item_id', None, db.ForeignKey('item.id'), primary_key=True),
    db.Column('discount_policy_id', None, db.ForeignKey('discount_policy.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow, nullable=False))


class DiscountPolicy(BaseScopedNameMixin, db.Model):
    """
    Consists of discount rules for prices applied on items
    """
    __tablename__ = 'discount_policy'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('organization_id', 'name'),
        db.CheckConstraint('item_quantity_min <= item_quantity_max', 'discount_policy_item_quantity_check'),
        db.CheckConstraint('percentage > 0 and percentage <= 100', 'discount_policy_percentage_check'))

    organization_id = db.Column(None, db.ForeignKey('organization.id'), nullable=False)
    organization = db.relationship(Organization, backref=db.backref('discount_policies', cascade='all, delete-orphan'))
    parent = db.synonym('organization')

    discount_type = db.Column(db.Integer, default=DISCOUNT_TYPES.AUTOMATIC, nullable=False)
    discount_code_base = db.Column(db.Unicode(20), nullable=True)

    # Minimum and maximum number of items for which the discount policy applies
    item_quantity_min = db.Column(db.Integer, default=1, nullable=False)
    item_quantity_max = db.Column(db.Integer, nullable=True)
    percentage = db.Column(db.Integer, nullable=False)
    items = db.relationship('Item', secondary=item_discount_policy)

    def __repr__(self):
        return u'<DiscountPolicy "{discount}">'.format(discount=self.title)

    def is_automatic(self):
        return self.discount_type == DISCOUNT_TYPES.AUTOMATIC

    def is_valid(self, quantity, coupons):
        return self.is_automatic_applicable() or self.is_coupon_applicable()

    @classmethod
    def get_from_item(cls, item, qty, coupons=[]):
        discounts = item.discount_policies.filter(DiscountPolicy.discount_type == DISCOUNT_TYPES.AUTOMATIC,
            or_(DiscountPolicy.item_quantity_min <= qty, and_(DiscountPolicy.item_quantity_min <= qty, DiscountPolicy.item_quantity_max > qty))).all()
        if not coupons:
            return discounts
        signer = Signer(app.config.get('SECRET_KEY'))
        coupon_bases = [signer.unsign(coupon) for coupon in coupons]
        for coupon_base in coupon_bases:
            discounts.append(item.discount_policies.filter_by(discount_code_base=coupon_base).first())
        return discounts


def generate_coupon_code(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class DiscountCoupon(IdMixin, db.Model):
    """
    Represents used discount coupons
    """
    __tablename__ = 'discount_coupon'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('code', 'discount_policy_id'),
        db.CheckConstraint('quantity_available <= quantity_total', 'discount_coupon_quantity_check'))

    code = db.Column(db.Unicode(20), nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)

    discount_policy_id = db.Column(None, db.ForeignKey('discount_policy.id'), nullable=False)
    discount_policy = db.relationship(DiscountPolicy, backref=db.backref('discount_coupons', cascade='all, delete-orphan'))
