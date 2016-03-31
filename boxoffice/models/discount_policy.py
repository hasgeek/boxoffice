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
    PRICE = (2, __("Price"))


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
        db.CheckConstraint('item_quantity_min <= item_quantity_max', 'discount_policy_item_quantity_check'),
        db.CheckConstraint('percentage > 0 and percentage <= 100', 'discount_policy_percentage_check'))

    organization_id = db.Column(None, db.ForeignKey('organization.id'), nullable=False)
    organization = db.relationship(Organization, backref=db.backref('discount_policies', cascade='all, delete-orphan'))
    parent = db.synonym('organization')

    discount_type = db.Column(db.Integer, default=DISCOUNT_TYPE.AUTOMATIC, nullable=False)

    # Minimum and maximum number of items for which the discount policy applies
    item_quantity_min = db.Column(db.Integer, default=1, nullable=False)
    item_quantity_max = db.Column(db.Integer, nullable=True)
    percentage = db.Column(db.Integer, nullable=False)
    items = db.relationship('Item', secondary=item_discount_policy)

    @cached_property
    def is_automatic(self):
        return self.discount_type == DISCOUNT_TYPE.AUTOMATIC

    @cached_property
    def is_coupon(self):
        return self.discount_type == DISCOUNT_TYPE.COUPON

    @classmethod
    def get_from_item(cls, item, qty, coupons=[]):
        """
        Returns a list of (discount_policy, discount_coupon) tuples
        applicable for an item, given the quantity of line items and coupons if any.
        """
        automatic_discounts = item.discount_policies.filter(DiscountPolicy.discount_type == DISCOUNT_TYPE.AUTOMATIC,
            db.or_(DiscountPolicy.item_quantity_min <= qty,
                db.and_(DiscountPolicy.item_quantity_min <= qty, DiscountPolicy.item_quantity_max > qty))).all()
        policies = [(discount, None) for discount in automatic_discounts]
        if not coupons:
            return policies

        for coupon in DiscountCoupon.get_valid_coupons(item.discount_policies, coupons):
            policies.append((coupon.discount_policy, coupon))
        return policies


def generate_coupon_code(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class DiscountCoupon(IdMixin, db.Model):
    __tablename__ = 'discount_coupon'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('discount_policy_id', 'code'),
        db.CheckConstraint('quantity_available <= quantity_total', 'discount_coupon_quantity_check'))

    code = db.Column(db.Unicode(20), nullable=False, default=generate_coupon_code)
    quantity_available = db.Column(db.Integer, default=0, nullable=False)
    quantity_total = db.Column(db.Integer, default=0, nullable=False)

    discount_policy_id = db.Column(None, db.ForeignKey('discount_policy.id'), nullable=False)
    discount_policy = db.relationship(DiscountPolicy, backref=db.backref('discount_coupons', cascade='all, delete-orphan'))

    @classmethod
    def get_valid_coupons(cls, discount_policies, codes):
        """
        Returns valid coupons, given a list of discount policies and discount codes
        """
        return cls.query.filter(cls.code.in_(codes),
            cls.quantity_available > 0,
            cls.discount_policy_id.in_([discount_policy.id
                for discount_policy in discount_policies.filter(DiscountPolicy.discount_type == DISCOUNT_TYPE.COUPON)])).all()

    def register_use(self):
        """
        Decrement the quantity available by 1 to register usage.
        """
        self.quantity_available -= 1
