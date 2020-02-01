# -*- coding: utf-8 -*-

import itertools
from decimal import Decimal
from ..models import DiscountPolicy, Item

__all__ = ['LineItemDiscounter']


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
            return []

        item = Item.query.get(line_items[0].item_id)
        if not item.is_available and not item.is_cancellable():
            # item unavailable, no discounts
            return []

        return DiscountPolicy.get_from_item(item, len(line_items), coupons)

    def calculate_discounted_amount(self, discount_policy, line_item):
        if line_item.base_amount is None:
            # item has expired, no discount
            return Decimal(0)

        if discount_policy.is_price_based:
            item = Item.query.get(line_item.item_id)
            discounted_price = item.discounted_price(discount_policy)
            if discounted_price is None:
                # no discounted price
                return Decimal(0)
            if discounted_price.amount >= line_item.base_amount:
                # No discount, base_amount is cheaper
                return Decimal(0)
            return line_item.base_amount - discounted_price.amount
        return (discount_policy.percentage * line_item.base_amount / Decimal(100))

    def is_coupon_usable(self, coupon, applied_to_count):
        return (coupon.usage_limit - coupon.used_count) > applied_to_count

    def apply_discount(self, policy_coupon, line_items, combo=False):
        """
        Returns the line_items with the given discount_policy and
        the discounted amount assigned to each line item.

        Assumes that the discount policies and discount coupons passed as arguments are valid and usable.
        """
        from .line_item import make_ntuple

        discounted_line_items = []
        # unpack (discount_policy, dicount_coupon)
        discount_policy, coupon = policy_coupon
        applied_to_count = 0
        for line_item in line_items:
            discounted_amount = self.calculate_discounted_amount(discount_policy, line_item)
            if (coupon and self.is_coupon_usable(coupon, applied_to_count) or discount_policy.is_automatic) and discounted_amount > 0 and (
                    not line_item.discount_policy_id or (combo and line_item.discounted_amount < discounted_amount)):
                # if the line item's assigned discount is lesser
                # than the current discount, assign the current discount to the line item
                discounted_line_items.append(make_ntuple(item_id=line_item.item_id,
                    base_amount=line_item.base_amount,
                    line_item_id=line_item.id if line_item.id else None,
                    discount_policy_id=discount_policy.id,
                    discount_coupon_id=coupon.id if coupon else None,
                    discounted_amount=discounted_amount,
                    final_amount=line_item.base_amount - discounted_amount))
                applied_to_count += 1
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
