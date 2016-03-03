import copy
import decimal
import itertools
from itsdangerous import Signer
from sqlalchemy import or_, and_
from boxoffice import app
from boxoffice.models import Item, DiscountPolicy, DISCOUNT_TYPES


def calculate_discounts(line_items, coupons=[]):
    """
    Given a list of line items, as named tuples or db objects,
    it calculates the applicable discounts and assigns the relevant discount
    policy_id to each line item.
    """
    if not line_items:
        return None

    valid_discounts = get_valid_discounts(line_items, coupons)
    if len(valid_discounts) > 1:
        return apply_max_discount(valid_discounts, line_items)
    elif len(valid_discounts) == 1:
        return apply_discount(valid_discounts[0], line_items)
    return line_items


def get_valid_discounts(line_items, coupons):
    """
    Returns all the applicable discounts given the quantity of items
    selected and any coupons.
    """
    qty = len(line_items)
    item = Item.query.get(line_items[0].item_id)
    query = item.discount_policies
    if not coupons:
        return query.filter(DiscountPolicy.discount_type == DISCOUNT_TYPES.AUTOMATIC,
            or_(DiscountPolicy.item_quantity_min <= qty,
                and_(DiscountPolicy.item_quantity_min <= qty, DiscountPolicy.item_quantity_max > qty))).all()

    signer = Signer(app.config.get('SECRET_KEY'))
    coupon_bases = [signer.unsign(coupon) for coupon in coupons]
    return query.filter(or_(DiscountPolicy.discount_code_base.in_(coupon_bases),
            DiscountPolicy.item_quantity_min <= qty,
            and_(DiscountPolicy.item_quantity_min <= qty, DiscountPolicy.item_quantity_max > qty))).all()


def apply_discount(discount, line_items, combo=False):
    """
    Returns the line_items with the given discount_policy assigned
    to each line item.
    """
    for idx, line_item in enumerate(line_items):
        discounted_amount = (discount.percentage*line_item.price/decimal.Decimal(100))
        if not line_item.discount_policy_id or (combo and line_item.discounted_amount < discounted_amount):
            line_item.discount_policy_id = discount.id
            line_item.discounted_amount = discounted_amount
        if discount.item_quantity_max and idx + 1 == discount.item_quantity_max:
            break
    return line_items


def apply_max_discount(discounts, line_items):
    """
    Fetches the various discount combinations and applies the discount policy
    combination that results in the maximum dicount for the given list of
    line items.
    """
    discounts.extend(get_combos(discounts, len(line_items)))
    discounted_line_items_list = []
    for discount in discounts:
        print type(discount)
        if isinstance(discount, tuple):
            # Combo discount
            combo_discounted_line_items = copy.deepcopy(line_items)
            for d in discount:
                combo_discounted_line_items = apply_discount(d, combo_discounted_line_items, combo=True)
            discounted_line_items_list.append(combo_discounted_line_items)
            print [li.discount_policy_id for li in combo_discounted_line_items]
        else:
            discounted_line_items_list.append(apply_discount(discount, line_items))

    return max(discounted_line_items_list, key=lambda line_item_list: sum([line_item.discounted_amount for line_item in line_item_list]))


def get_combos(discounts, qty):
    """
    Returns the various valid discount combinations given a list of discount policies
    """
    valid_combos = []
    for n in range(2, len(discounts) + 1):
        combos = list(itertools.combinations(discounts, n))
        if qty >= sum([discount.item_quantity_min for combo in combos for discount in combo]):
            valid_combos.extend(combos)
    return valid_combos
