import decimal
import itertools
from boxoffice.models import Item, DiscountPolicy


def calculate_discounts(line_items, coupons=[]):
    """
    Given a list of line items, as named tuples or db objects,
    each supplied with an `item_id` and a `price`, this function,
    calculates the applicable discounts and assigns the relevant discount
    policy_id and the discounted amount to each line item.
    """
    if not line_items:
        return None

    valid_discounts = get_valid_discounts(line_items, coupons)
    if len(valid_discounts) > 1:
        # Multiple discounts found, find the combination that results
        # in the best discount
        return apply_max_discount(valid_discounts, line_items)
    elif len(valid_discounts) == 1:
        return apply_discount(valid_discounts[0], line_items)
    for line_item in line_items:
        line_item.discounted_amount = decimal.Decimal(0)
    return line_items


def get_valid_discounts(line_items, coupons):
    """
    Returns all the applicable discounts given the quantity of items
    selected and any coupons.
    """
    if not line_items:
        return None

    item = Item.query.get(line_items[0].item_id)
    if not coupons:
        return DiscountPolicy.get_from_item(item, len(line_items))
    return DiscountPolicy.get_from_item(item, len(line_items), coupons)


def calculate_discounted_amount(percentage, base_amount):
    return (percentage * base_amount/decimal.Decimal(100)) or decimal.Decimal(0)


def apply_discount(discount, line_items, combo=False):
    """
    Returns the line_items with the given discount_policy and
    the discounted amount assigned to each line item.
    """
    for idx, line_item in enumerate(line_items):
        discounted_amount = calculate_discounted_amount(discount.percentage, line_item.base_amount)
        print discounted_amount
        if not line_item.discount_policy_id or (combo and line_item.discounted_amount < discounted_amount):
            line_item.discount_policy_id = discount.id
            line_item.discounted_amount = discounted_amount
        if discount.item_quantity_max and idx + 1 == discount.item_quantity_max:
            # If the upper limit on the discount's allowed item quantity
            # is reached, break out of the loop.
            break
    return line_items


def apply_combo_discount(discounts, line_items):
    """
    Applies multiple discounts to a list of line items recursively.
    """
    if len(discounts) == 0:
        return line_items
    if len(discounts) == 1:
        return apply_discount(discounts[0], line_items, combo=True)
    return apply_combo_discount([discounts[0]], apply_combo_discount(discounts[1:], line_items))


def apply_max_discount(discounts, line_items):
    """
    Fetches the various discount combinations and applies the discount policy
    combination that results in the maximum dicount for the given list of
    line items.
    """
    discounts.extend(get_combos(discounts, len(line_items)))
    discounted_line_items_list = []

    for discount in discounts:
        if isinstance(discount, tuple):
            # Combo discount
            discounted_line_items_list.append(apply_combo_discount(discount, line_items))
        else:
            discounted_line_items_list.append(apply_discount(discount, line_items))

    return max(discounted_line_items_list,
        key=lambda line_item_list: sum([line_item.discounted_amount for line_item in line_item_list]))


def get_combos(discounts, qty):
    """
    Returns the various valid discount combinations given a list of discount policies
    """
    valid_combos = []
    # Get all possible valid combinations of discounts in groups of 2..n,
    # where n is the number of discounts
    for n in range(2, len(discounts) + 1):
        combos = list(itertools.combinations(discounts, n))
        if qty >= sum([discount.item_quantity_min for combo in combos for discount in combo]):
            # if number of line items is gte to number of items the discount policies
            # as a combo supports, count it as a valid combo
            valid_combos.extend(combos)
    return valid_combos
