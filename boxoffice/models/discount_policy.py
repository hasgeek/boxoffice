import string
import random
from datetime import datetime
from werkzeug import cached_property
from baseframe import __
from coaster.utils import LabeledEnum
from boxoffice.models import db, BaseScopedNameMixin, IdMixin
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
    """
    __tablename__ = 'discount_policy'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('organization_id', 'name'),
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
    items = db.relationship('Item', secondary=item_discount_policy)

    @cached_property
    def is_automatic(self):
        return self.discount_type == DISCOUNT_TYPE.AUTOMATIC

    @cached_property
    def is_coupon(self):
        return self.discount_type == DISCOUNT_TYPE.COUPON

    @classmethod
    def get_from_item(cls, item, qty, coupon_codes=[]):
        """
        Returns a list of (discount_policy, discount_coupon) tuples
        applicable for an item, given the quantity of line items and coupons if any.
        """
        automatic_discounts = item.discount_policies.filter(DiscountPolicy.discount_type == DISCOUNT_TYPE.AUTOMATIC,
            DiscountPolicy.item_quantity_min <= qty).all()
        policies = [(discount, None) for discount in automatic_discounts]
        if not coupon_codes:
            return policies
        else:
            coupon_policies = item.discount_policies.filter(DiscountPolicy.discount_type == DISCOUNT_TYPE.COUPON).all()
            coupon_policy_ids = [cp.id for cp in coupon_policies]
            for coupon_code in coupon_codes:
                coupon = DiscountCoupon.query.filter(DiscountCoupon.discount_policy_id.in_(coupon_policy_ids), DiscountCoupon.code==coupon_code).one_or_none()
                print len([line_item for line_item in item.line_items if line_item.discount_coupon == coupon])
                if coupon and coupon.usage_limit > len([line_item for line_item in item.line_items if line_item.discount_coupon == coupon]):
                    policies.append((coupon.discount_policy, coupon))

        return policies


def generate_coupon_code(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class DiscountCoupon(IdMixin, db.Model):
    __tablename__ = 'discount_coupon'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('discount_policy_id', 'code'),)

    code = db.Column(db.Unicode(20), nullable=False, default=generate_coupon_code)
    usage_limit = db.Column(db.Integer, nullable=True, default=1)

    discount_policy_id = db.Column(None, db.ForeignKey('discount_policy.id'), nullable=False)
    discount_policy = db.relationship(DiscountPolicy, backref=db.backref('discount_coupons', cascade='all, delete-orphan'))
