import itertools
from decimal import Decimal
from collections import namedtuple
from boxoffice.models import db, BaseMixin, Order, Item, DiscountPolicy
from coaster.utils import LabeledEnum
from baseframe import __

__all__ = ['LineItem']


class LINE_ITEM_STATUS(LabeledEnum):
    CONFIRMED = (0, __("Confirmed"))
    CANCELLED = (1, __("Cancelled"))


def make_ntuple(item_id, base_amount, **kwargs):
    line_item_tup = namedtuple('LineItem', ['item_id', 'base_amount', 'discount_policy_id', 'discount_coupon_id', 'discounted_amount'])
    return line_item_tup(item_id,
        base_amount,
        kwargs.get('discount_policy_id', None),
        kwargs.get('discount_coupon_id', None),
        kwargs.get('discounted_amount', Decimal(0)))


class LineItem(BaseMixin, db.Model):
    """
    Note: Line Items MUST NOT be deleted.
    They must only be cancelled.
    """
    __tablename__ = 'line_item'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('customer_order_id', 'line_item_seq'),)

    customer_order_id = db.Column(None, db.ForeignKey('customer_order.id'), nullable=False)
    order = db.relationship(Order, backref=db.backref('line_items', cascade='all, delete-orphan'))
    # line_item_seq is the relative number of the line item per order.
    line_item_seq = db.Column(db.Integer, nullable=False)

    item_id = db.Column(None, db.ForeignKey('item.id'), nullable=False)
    item = db.relationship(Item, backref=db.backref('line_items', cascade='all, delete-orphan'))

    discount_policy_id = db.Column(None, db.ForeignKey('discount_policy.id'), nullable=True)
    discount_policy = db.relationship('DiscountPolicy', backref=db.backref('line_items'))

    discount_coupon_id = db.Column(None, db.ForeignKey('discount_coupon.id'), nullable=True)
    discount_coupon = db.relationship('DiscountCoupon', backref=db.backref('line_items'))

    base_amount = db.Column(db.Numeric, default=Decimal(0), nullable=False)
    discounted_amount = db.Column(db.Numeric, default=Decimal(0), nullable=False)
    final_amount = db.Column(db.Numeric, default=Decimal(0), nullable=False)
    status = db.Column(db.Integer, default=LINE_ITEM_STATUS.CONFIRMED, nullable=False)
    ordered_at = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)

    @classmethod
    def calculate(cls, line_item_dicts, coupons=[]):
        """
        Returns line item tuples with the respective base_amount, discounted_amount,
        final_amount, discount_policy and discount coupon populated
        """
        item_line_items = {}
        line_items = []
        for line_item_dict in line_item_dicts:
            item = Item.query.get(line_item_dict['item_id'])
            if not item_line_items.get(unicode(item.id)):
                item_line_items[unicode(item.id)] = []
            item_line_items[unicode(item.id)].append(make_ntuple(item_id=item.id,
                base_amount=item.current_price().amount))
        coupon_list = list(set(coupons)) if coupons else []
        discounter = LineItemDiscounter()
        for item_id in item_line_items.keys():
            item_line_items[item_id] = discounter.get_discounted_line_items(item_line_items[item_id], coupon_list)
            line_items.extend(item_line_items[item_id])
        return line_items


class LineItemDiscounter():
    def get_discounted_line_items(self, line_items, coupons=[]):
        """
        Returns line items with the maximum possible discount applied.
        """
        if not line_items:
            return None
        if len(set(line_item.item_id for line_item in line_items)) > 1:
            raise ValueError("line_items must be of the same item_id")

        valid_discounts = self.get_valid_discounts(line_items, coupons)
        if len(valid_discounts) > 1:
            # Multiple discounts found, find the combination of discounts that results
            # in the maximum discount and apply those discounts to the line items.
            return self.apply_max_discount(valid_discounts, line_items)
        elif len(valid_discounts) == 1:
            return self.apply_discount(valid_discounts[0], line_items)
        return line_items

    def get_valid_discounts(self, line_items, coupons):
        """
        Returns all the applicable discounts given the quantity of items
        selected and any coupons.
        """
        if not line_items:
            return None

        item = Item.query.get(line_items[0].item_id)
        return DiscountPolicy.get_from_item(item, len(line_items), coupons)

    def calculate_discounted_amount(self, discount_policy, line_item):
        if discount_policy.is_price_based:
            item = Item.query.get(line_item.item_id)
            discounted_price = item.discounted_price(discount_policy).amount
            if discounted_price >= line_item.base_amount:
                # No discount, base_amount is cheaper
                return Decimal(0)
            return line_item.base_amount - discounted_price
        return (discount_policy.percentage * line_item.base_amount/Decimal(100))

    def apply_discount(self, policy_coupon, line_items, combo=False):
        """
        Returns the line_items with the given discount_policy and
        the discounted amount assigned to each line item.

        Assumes that the discount policies and discount coupons passed as arguments are valid and usable.
        """
        discounted_line_items = []
        coupon_used = False
        # unpack (discount_policy, dicount_coupon)
        discount_policy, coupon = policy_coupon
        for line_item in line_items:
            discounted_amount = self.calculate_discounted_amount(discount_policy, line_item)
            if ((coupon and (coupon.unlimited or not coupon_used)) or discount_policy.is_automatic) and discounted_amount > 0 and (
                    not line_item.discount_policy_id or (combo and line_item.discounted_amount < discounted_amount)):
                # if the line item's assigned discount is lesser
                # than the current discount, assign the current discount to the line item
                if coupon:
                    discount_coupon_id = coupon.id
                    coupon_used = True
                else:
                    discount_coupon_id = None
                discounted_line_items.append(make_ntuple(item_id=line_item.item_id,
                    base_amount=line_item.base_amount,
                    discount_policy_id=discount_policy.id,
                    discount_coupon_id=discount_coupon_id,
                    discounted_amount=discounted_amount))

            else:
                # Current discount is not applicable, copy over the line item as it is.
                discounted_line_items.append(line_item)
        return discounted_line_items

    def apply_combo_discount(self, discounts, line_items):
        """
        Applies multiple discounts to a list of line items recursively.
        """
        if len(discounts) == 0:
            return line_items
        if len(discounts) == 1:
            return self.apply_discount(discounts[0], line_items, combo=True)
        return self.apply_combo_discount([discounts[0]], self.apply_combo_discount(discounts[1:], line_items))

    def apply_max_discount(self, discounts, line_items):
        """
        Fetches the various discount combinations and applies the discount policy
        combination that results in the maximum discount for the given list of
        line items.
        """
        discounts.extend(self.get_combos(discounts, len(line_items)))
        discounted_line_items_list = []

        for discount in discounts:
            if isinstance(discount[0], tuple):
                # Combo discount
                discounted_line_items_list.append(self.apply_combo_discount(discount, line_items))
            else:
                discounted_line_items_list.append(self.apply_discount(discount, line_items))
        return max(discounted_line_items_list,
            key=lambda line_item_list: sum([line_item.discounted_amount for line_item in line_item_list]))

    def get_combos(self, discounts, qty):
        """
        Returns the various valid discount combinations given a list of discount policies
        """
        valid_combos = []
        if len(discounts) < 2:
            return valid_combos

        # Get all possible valid combinations of discounts in groups of 2..n,
        # where n is the number of discounts
        for n in range(2, len(discounts) + 1):
            combos = list(itertools.combinations(discounts, n))
            for combo in combos:
                if sum([discount.item_quantity_min for discount, coupon in combo]) <= qty:
                    # if number of line items is gte to number of items the discount policies
                    # as a combo supports, count it as a valid combo
                    valid_combos.append(combo)
        return valid_combos
