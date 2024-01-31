from __future__ import annotations

from decimal import Decimal
from typing import List, Sequence, Union, cast
from uuid import UUID
import itertools

from beartype import beartype

from .discount_policy import DiscountCoupon, DiscountPolicy, PolicyCoupon
from .line_item import LineItemTuple

__all__ = ['LineItemDiscounter']


class LineItemDiscounter:
    @beartype
    def get_discounted_line_items(
        self,
        line_items: Sequence[LineItemTuple],
        coupons: Sequence[str] = (),
    ) -> Sequence[LineItemTuple]:
        """Return line items with the maximum possible discount applied."""
        if not line_items:
            return []
        if len({line_item.ticket_id for line_item in line_items}) > 1:
            raise ValueError("line_items must be of the same ticket_id")

        valid_discounts = self.get_valid_discounts(line_items, coupons)
        if len(valid_discounts) > 1:
            # Multiple discounts found, find the combination of discounts that results
            # in the maximum discount and apply those discounts to the line items.
            return self.apply_max_discount(valid_discounts, line_items)
        if len(valid_discounts) == 1:
            return self.apply_discount(valid_discounts[0], line_items)
        return line_items

    @beartype
    def get_valid_discounts(
        self, line_items: Sequence[LineItemTuple], coupons: Sequence[str]
    ) -> Sequence[PolicyCoupon]:
        """Return available discounts given line items and coupon codes."""
        if not line_items:
            return []

        ticket = Item.query.get(line_items[0].ticket_id)
        if ticket is None or not ticket.is_available and not ticket.is_cancellable():
            # Ticket unavailable, no discounts
            return []

        return DiscountPolicy.get_from_ticket(ticket, len(line_items), coupons)

    @beartype
    def calculate_discounted_amount(
        self, discount_policy: DiscountPolicy, line_item: LineItemTuple
    ) -> Decimal:
        if line_item.base_amount is None or line_item.base_amount == Decimal(0):
            # Ticket has expired, no discount
            return Decimal(0)

        if discount_policy.is_price_based:
            ticket = Item.query.get(line_item.ticket_id)
            if ticket is None:  # Failsafe flagged by static type checker
                return Decimal(0)
            discounted_price = ticket.discounted_price(discount_policy)
            if discounted_price is None:
                # no discounted price
                return Decimal(0)
            if discounted_price.amount >= line_item.base_amount:
                # No discount, base_amount is cheaper
                return Decimal(0)
            return line_item.base_amount - discounted_price.amount
        return (discount_policy.percentage or 0) * line_item.base_amount / Decimal(100)

    @beartype
    def is_coupon_usable(self, coupon: DiscountCoupon, applied_to_count: int) -> bool:
        return (coupon.usage_limit - coupon.used_count) > applied_to_count

    @beartype
    def apply_discount(
        self,
        policy_coupon: PolicyCoupon,
        line_items: Sequence[LineItemTuple],
        combo: bool = False,
    ) -> Sequence[LineItemTuple]:
        """
        Apply discounts on given line items.

        Return line_items with the given discount_policy and
        the discounted amount assigned to each line item.

        Assumes that the discount policies and discount coupons passed as arguments are
        valid and usable.
        """
        discounted_line_items: List[LineItemTuple] = []
        applied_to_count = 0
        for line_item in line_items:
            discounted_amount = self.calculate_discounted_amount(
                policy_coupon.policy, line_item
            )
            if (
                (  # pylint: disable=too-many-boolean-expressions
                    policy_coupon.coupon
                    and self.is_coupon_usable(policy_coupon.coupon, applied_to_count)
                    or policy_coupon.policy.is_automatic
                )
                and discounted_amount > 0
                and (
                    not line_item.discount_policy_id
                    or (combo and line_item.discounted_amount < discounted_amount)
                )
            ):
                # if the line item's assigned discount is lesser than the current
                # discount, assign the current discount to the line item
                discounted_line_items.append(
                    LineItemTuple(
                        id=cast(UUID, line_item.id) if line_item.id else None,
                        ticket_id=line_item.ticket_id,
                        base_amount=line_item.base_amount,
                        discount_policy_id=cast(UUID, policy_coupon.policy.id),
                        discount_coupon_id=(
                            cast(UUID, policy_coupon.coupon.id)
                            if policy_coupon.coupon
                            else None
                        ),
                        discounted_amount=discounted_amount,
                        final_amount=line_item.base_amount - discounted_amount,
                    )
                )
                applied_to_count += 1
            else:
                # Current discount is not applicable, copy over the line item as it is.
                discounted_line_items.append(line_item)
        return discounted_line_items

    @beartype
    def apply_combo_discount(
        self,
        discounts: List[PolicyCoupon],
        line_items: Sequence[LineItemTuple],
    ) -> Sequence[LineItemTuple]:
        """Apply multiple discounts to a list of line items recursively."""
        if len(discounts) == 0:
            return line_items
        if len(discounts) == 1:
            return self.apply_discount(discounts[0], line_items, combo=True)
        return self.apply_combo_discount(
            [discounts[0]], self.apply_combo_discount(discounts[1:], line_items)
        )

    @beartype
    def apply_max_discount(
        self,
        discounts: List[
            Union[
                PolicyCoupon,
                Sequence[PolicyCoupon],
            ]
        ],
        line_items: Sequence[LineItemTuple],
    ) -> Sequence[LineItemTuple]:
        """
        Find and apply the maximum discount available.

        Fetches the various discount combinations and applies the discount policy
        combination that results in the maximum discount for the given list of
        line items.
        """
        discounts.extend(self.get_combos(discounts, len(line_items)))
        discounted_line_items_list: List[Sequence[LineItemTuple]] = []

        for discount in discounts:
            if isinstance(discount, list):
                # Combo discount
                discounted_line_items_list.append(
                    self.apply_combo_discount(discount, line_items)
                )
            else:
                discounted_line_items_list.append(
                    self.apply_discount(discount, line_items)
                )
        return max(
            discounted_line_items_list,
            key=lambda line_item_list: sum(
                line_item.discounted_amount for line_item in line_item_list
            ),
        )

    @beartype
    def get_combos(
        self, discounts: List[PolicyCoupon], qty: int
    ) -> List[List[PolicyCoupon]]:
        """Return valid discount combinations given a list of discount policies."""
        valid_combos: List[List[PolicyCoupon]] = []
        if len(discounts) < 2:
            return valid_combos

        # Get all possible valid combinations of discounts in groups of 2..n,
        # where n is the number of discounts
        for n in range(2, len(discounts) + 1):
            combos = list(itertools.combinations(discounts, n))
            for combo in combos:
                if sum(pc.policy.item_quantity_min for pc in combo) <= qty:
                    # if number of line items is gte to number of items the discount
                    # policies as a combo supports, count it as a valid combo
                    valid_combos.append(list(combo))
        return valid_combos


# Tail imports
from .item import Item  # isort:skip
