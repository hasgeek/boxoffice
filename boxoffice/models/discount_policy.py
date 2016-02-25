import string
import random
from datetime import datetime
from sqlalchemy import event, DDL
from baseframe import __
from coaster.utils import LabeledEnum
from boxoffice.models import db, BaseMixin, BaseScopedNameMixin, IdMixin
from boxoffice.models import Organization


# __all__ = ['DiscountPolicy', 'DiscountCoupon', 'DiscountOffer', 'item_discount_policy']
__all__ = ['DiscountPolicy', 'DiscountCoupon', 'item_discount_policy']


class DISCOUNT_TYPES(LabeledEnum):
    AUTOMATIC = (0, __("Automatic"))
    COUPON = (1, __("Coupon"))
    USER = (2, __("User"))


item_discount_policy = db.Table('item_discount_policy', db.Model.metadata,
    db.Column('item_id', None, db.ForeignKey('item.id'), primary_key=True),
    db.Column('discount_policy_id', None, db.ForeignKey('discount_policy.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow, nullable=False))


# class DiscountOffer(BaseMixin, db.Model):
#     discount_policy_id = db.Column('discount_policy_id', None, db.ForeignKey('discount_policy.id'), primary_key=True)
#     discount_policy = db.relationship('DiscountPolicy', backref=db.backref('discount_offers', cascade='all, delete-orphan'))
#     user_id = db.Column(None, db.ForeignKey('user.id'), nullable=True)
#     user = db.relationship('User', backref=db.backref('discount_offers', cascade='all, delete-orphan'))
#     availed_at = db.Column(db.DateTime, nullable=True)

#     def avail(self):
#         self.availed_at = datetime.utcnow()


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

    # Minimum and maximum number of items for which the discount policy applies
    item_quantity_min = db.Column(db.Integer, default=1, nullable=False)
    item_quantity_max = db.Column(db.Integer, nullable=True)
    percentage = db.Column(db.Integer, nullable=False)
    items = db.relationship('Item', secondary=item_discount_policy)
    # users = db.relationship('User', secondary='discount_offer', backref='discount_policies', lazy='dynamic')

    def __repr__(self):
        return u'<DiscountPolicy "{discount}">'.format(discount=self.title)

    # def is_applicable_to_user(self, user):
    #     """
    #     Checks if a discount policy is applicable to a given user
    #     """
    #     offer = DiscountOffer.query.get(self, user)
    #     return user in self.users and not offer.availed_at

    def is_valid(self, quantity):
        """
        Checks if a discount policy is valid for a line item, given its quantity
        """
        is_min = quantity >= self.item_quantity_min
        if not self.item_quantity_max:
            return is_min
        else:
            return is_min and quantity <= self.item_quantity_max


def generate_coupon_code(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class DiscountCoupon(IdMixin, db.Model):
    __tablename__ = 'discount_coupon'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('code', 'discount_policy_id'),
        db.CheckConstraint('quantity_available <= quantity_total', 'discount_coupon_quantity_check'))

    code = db.Column(db.Unicode(20), default=generate_coupon_code, nullable=False)

    discount_policy_id = db.Column(None, db.ForeignKey('discount_policy.id'), nullable=False)
    discount_policy = db.relationship(DiscountPolicy, backref=db.backref('discount_coupons', cascade='all, delete-orphan'))

    quantity_available = db.Column(db.Integer, default=0, nullable=False)
    quantity_total = db.Column(db.Integer, default=0, nullable=False)

create_discount_coupon_index = DDL(
    'CREATE INDEX ix_discount_coupon_code ON "discount_coupon" (lower(code) varchar_pattern_ops); ')
event.listen(DiscountCoupon.__table__, 'after_create',
    create_discount_coupon_index.execute_if(dialect='postgresql'))
