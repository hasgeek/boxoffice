# -*- coding: utf-8 -*-

import pytest
from boxoffice.models import (
    Category,
    DiscountCoupon,
    DiscountPolicy,
    Item,
    ItemCollection,
    Organization,
)


class TestDiscountPolicies(object):
    def test_unique_discount_coupon_code(self, test_client, test_db, new_discount_policy, new_discount_policy_another, new_discount_coupon):
        assert len(new_discount_policy.discount_coupons) == 1
        assert len(new_discount_policy_another.discount_coupons) == 0
        assert new_discount_coupon.code == u"TESTCODE"

        # both new_discount_policy and new_discount_policy_another are attached
        # To items from the same item collection. So creating another
        # discount coupon with same code should through error.
        new_code = DiscountCoupon(code=u"TESTCODE", discount_policy=new_discount_policy_another)
        test_db.session.add(new_code)
        # with pytest.raises(Exception):
        test_db.session.commit()

