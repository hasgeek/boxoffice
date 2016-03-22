import decimal
import json
import unittest
from flask import url_for
from boxoffice import app, init_for
from boxoffice.models import (db)
from fixtures import init_data
from boxoffice.models import Item, DiscountPolicy, DiscountCoupon


class TestKharchaAPI(unittest.TestCase):

    def setUp(self):
        self.ctx = app.test_request_context()
        self.ctx.push()
        init_for('test')
        db.drop_all()
        db.create_all()
        init_data()
        self.client = app.test_client()

    def test_undiscounted_kharcha(self):
        first_item = Item.query.filter_by(name='conference-ticket').first()
        undiscounted_quantity = 2
        kharcha_req = {'line_items': [{'item_id': unicode(first_item.id), 'quantity': undiscounted_quantity}]}
        resp = self.client.post(url_for('kharcha'), data=json.dumps(kharcha_req), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])

        self.assertEquals(resp.status_code, 200)
        resp_json = json.loads(resp.get_data())
        # Test that the price is correct
        self.assertEquals(resp_json.get('line_items')[unicode(first_item.id)].get('final_amount'),
            undiscounted_quantity * first_item.current_price().amount)

        policy_ids = [policy for policy in resp_json.get('line_items')[unicode(first_item.id)].get('discount_policy_ids')]
        self.assertEquals(resp_json.get('line_items')[unicode(first_item.id)].get('final_amount'), undiscounted_quantity * first_item.current_price().amount)
        expected_discount_policy_ids = []
        self.assertEquals(expected_discount_policy_ids, policy_ids)

    def test_discounted_bulk_kharcha(self):
        first_item = Item.query.filter_by(name='conference-ticket').first()
        discounted_quantity = 10
        kharcha_req = {'line_items': [{'item_id': unicode(first_item.id), 'quantity': discounted_quantity}]}
        resp = self.client.post(url_for('kharcha'), data=json.dumps(kharcha_req), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])
        self.assertEquals(resp.status_code, 200)
        resp_json = json.loads(resp.get_data())

        base_amount = discounted_quantity * first_item.current_price().amount
        discounted_amount = (first_item.discount_policies[0].percentage * base_amount)/decimal.Decimal(100.0)
        self.assertEquals(resp_json.get('line_items')[unicode(first_item.id)].get('final_amount'),
            base_amount-discounted_amount)

        expected_discount_policy_ids = [unicode(DiscountPolicy.query.filter_by(title='10% discount on rootconf').first().id)]
        policy_ids = [unicode(policy) for policy in resp_json.get('line_items')[unicode(first_item.id)].get('discount_policy_ids')]

        # Test that all the discount policies are returned
        for expected_policy_id in expected_discount_policy_ids:
            self.assertIn(expected_policy_id, [policy for policy in policy_ids])

    def test_discounted_coupon_kharcha(self):
        first_item = Item.query.filter_by(name='conference-ticket').first()
        coupon = DiscountCoupon.query.filter_by(code='coupon1').first()
        discounted_quantity = 1
        kharcha_req = {'line_items': [{'item_id': unicode(first_item.id), 'quantity': discounted_quantity}], 'discount_coupons': [coupon.code]}
        resp = self.client.post(url_for('kharcha'), data=json.dumps(kharcha_req), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])
        self.assertEquals(resp.status_code, 200)
        resp_json = json.loads(resp.get_data())

        base_amount = discounted_quantity * first_item.current_price().amount
        discounted_amount = (coupon.discount_policy.percentage * base_amount)/decimal.Decimal(100.0)
        self.assertEquals(resp_json.get('line_items')[unicode(first_item.id)].get('final_amount'),
            base_amount-discounted_amount)

        expected_discount_policy_ids = [unicode(coupon.discount_policy_id)]
        policy_ids = [unicode(policy) for policy in resp_json.get('line_items')[unicode(first_item.id)].get('discount_policy_ids')]

        # Test that all the discount policies are returned
        for expected_policy_id in expected_discount_policy_ids:
            self.assertIn(expected_policy_id, [policy for policy in policy_ids])

    def test_discounted_complex_kharcha(self):
        first_item = Item.query.filter_by(name='conference-ticket').first()
        discounted_quantity = 9
        coupon2 = DiscountCoupon.query.filter_by(code='coupon2').first()
        coupon3 = DiscountCoupon.query.filter_by(code='coupon3').first()
        kharcha_req = {'line_items': [{'item_id': unicode(first_item.id), 'quantity': discounted_quantity}], 'discount_coupons': [coupon2.code, coupon3.code]}

        resp = self.client.post(url_for('kharcha'), data=json.dumps(kharcha_req), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])

        self.assertEquals(resp.status_code, 200)
        resp_json = json.loads(resp.get_data())

        base_amount = discounted_quantity * first_item.current_price().amount
        discounted_amount = 2*first_item.current_price().amount
        self.assertEquals(resp_json.get('line_items')[unicode(first_item.id)].get('final_amount'),
            base_amount-discounted_amount)

        expected_discount_policy_ids = [unicode(coupon2.discount_policy_id), unicode(coupon3.discount_policy_id)]
        policy_ids = [unicode(policy) for policy in resp_json.get('line_items')[unicode(first_item.id)].get('discount_policy_ids')]
        # Test that all the discount policies are returned
        for expected_policy_id in expected_discount_policy_ids:
            self.assertIn(expected_policy_id, [policy for policy in policy_ids])

    def tearDown(self):
        db.session.rollback()
        db.drop_all()
        self.ctx.pop()
