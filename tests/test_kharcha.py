# -*- coding: utf-8 -*-

import decimal
import json
import unittest
from flask import url_for
from coaster.utils import make_name
from boxoffice import app
from boxoffice.models import (db)
from .fixtures import init_data
from boxoffice.models import Item, DiscountPolicy, DiscountCoupon


class TestKharchaAPI(unittest.TestCase):

    def setUp(self):
        self.ctx = app.test_request_context()
        self.ctx.push()
        init_data()
        self.client = app.test_client()

    def test_undiscounted_kharcha(self):
        first_item = Item.query.filter_by(name='conference-ticket').first()
        undiscounted_quantity = 2
        kharcha_req = {'line_items': [{'item_id': str(first_item.id), 'quantity': undiscounted_quantity}]}
        resp = self.client.post(url_for('kharcha'), data=json.dumps(kharcha_req), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])

        self.assertEqual(resp.status_code, 200)
        resp_json = json.loads(resp.get_data())
        # Test that the price is correct
        self.assertEqual(resp_json.get('line_items')[str(first_item.id)].get('final_amount'),
            undiscounted_quantity * first_item.current_price().amount)

        policy_ids = [policy for policy in resp_json.get('line_items')[str(first_item.id)].get('discount_policy_ids')]
        self.assertEqual(resp_json.get('line_items')[str(first_item.id)].get('final_amount'), undiscounted_quantity * first_item.current_price().amount)
        expected_discount_policy_ids = []
        self.assertEqual(expected_discount_policy_ids, policy_ids)

    def test_expired_item_kharcha(self):
        expired_ticket = Item.query.filter_by(name='expired-ticket').first()
        quantity = 2
        kharcha_req = {'line_items': [{'item_id': str(expired_ticket.id), 'quantity': quantity}]}
        resp = self.client.post(url_for('kharcha'), data=json.dumps(kharcha_req), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])

        self.assertEqual(resp.status_code, 200)
        resp_json = json.loads(resp.get_data())
        # Test that the price is None
        self.assertEqual(resp_json.get('line_items')[str(expired_ticket.id)].get('base_amount'), None)

    def test_expired_discounted_item_kharcha(self):
        expired_ticket = Item.query.filter_by(name='expired-ticket').first()
        quantity = 2
        coupon = DiscountCoupon.query.filter_by(code='couponex').first()
        # import IPython; IPython.embed()
        kharcha_req = {'line_items': [{'item_id': str(expired_ticket.id), 'quantity': quantity}], 'discount_coupons': [coupon.code]}
        resp = self.client.post(url_for('kharcha'), data=json.dumps(kharcha_req), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])

        self.assertEqual(resp.status_code, 200)
        resp_json = json.loads(resp.get_data())
        # Test that the price is None
        self.assertEqual(resp_json.get('line_items')[str(expired_ticket.id)].get('base_amount'), None)

    def test_discounted_bulk_kharcha(self):
        first_item = Item.query.filter_by(name='conference-ticket').first()
        discounted_quantity = 10
        kharcha_req = {'line_items': [{'item_id': str(first_item.id), 'quantity': discounted_quantity}]}
        resp = self.client.post(url_for('kharcha'), data=json.dumps(kharcha_req), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])
        self.assertEqual(resp.status_code, 200)
        resp_json = json.loads(resp.get_data())

        base_amount = discounted_quantity * first_item.current_price().amount
        discounted_amount = (first_item.discount_policies[0].percentage * base_amount) / decimal.Decimal(100.0)
        self.assertEqual(resp_json.get('line_items')[str(first_item.id)].get('final_amount'),
            base_amount - discounted_amount)

        expected_discount_policy_ids = [str(DiscountPolicy.query.filter_by(title='10% discount on rootconf').first().id)]
        policy_ids = [str(policy) for policy in resp_json.get('line_items')[str(first_item.id)].get('discount_policy_ids')]

        # Test that all the discount policies are returned
        for expected_policy_id in expected_discount_policy_ids:
            self.assertIn(expected_policy_id, [policy for policy in policy_ids])

    def test_discounted_coupon_kharcha(self):
        first_item = Item.query.filter_by(name='conference-ticket').first()
        coupon = DiscountCoupon.query.filter_by(code='coupon1').first()
        discounted_quantity = 1
        kharcha_req = {'line_items': [{'item_id': str(first_item.id), 'quantity': discounted_quantity}], 'discount_coupons': [coupon.code]}
        resp = self.client.post(url_for('kharcha'), data=json.dumps(kharcha_req), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])
        self.assertEqual(resp.status_code, 200)
        resp_json = json.loads(resp.get_data())

        base_amount = discounted_quantity * first_item.current_price().amount
        discounted_amount = (coupon.discount_policy.percentage * base_amount) / decimal.Decimal(100.0)
        self.assertEqual(resp_json.get('line_items')[str(first_item.id)].get('final_amount'),
            base_amount - discounted_amount)

        expected_discount_policy_ids = [str(coupon.discount_policy_id)]
        policy_ids = [str(policy) for policy in resp_json.get('line_items')[str(first_item.id)].get('discount_policy_ids')]

        # Test that all the discount policies are returned
        for expected_policy_id in expected_discount_policy_ids:
            self.assertIn(expected_policy_id, [policy for policy in policy_ids])

    def test_signed_discounted_coupon_kharcha(self):
        first_item = Item.query.filter_by(name='conference-ticket').first()
        signed_policy = DiscountPolicy.query.filter_by(name='signed').first()
        code = signed_policy.gen_signed_code()
        discounted_quantity = 2
        kharcha_req = {'line_items': [{'item_id': str(first_item.id), 'quantity': discounted_quantity}], 'discount_coupons': [code]}
        resp = self.client.post(url_for('kharcha'), data=json.dumps(kharcha_req), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])
        self.assertEqual(resp.status_code, 200)
        resp_json = json.loads(resp.get_data())

        base_amount = discounted_quantity * first_item.current_price().amount
        discounted_amount = (signed_policy.percentage * base_amount) / decimal.Decimal(100.0)
        self.assertEqual(resp_json.get('line_items')[str(first_item.id)].get('final_amount'),
            base_amount - discounted_amount)

        expected_discount_policy_ids = [str(signed_policy.id)]
        policy_ids = [str(policy) for policy in resp_json.get('line_items')[str(first_item.id)].get('discount_policy_ids')]

        # Test that all the discount policies are returned
        for expected_policy_id in expected_discount_policy_ids:
            self.assertIn(expected_policy_id, [policy for policy in policy_ids])

    def test_unlimited_coupon_kharcha(self):
        first_item = Item.query.filter_by(name='conference-ticket').first()
        coupon_code = 'unlimited'
        discounted_quantity = 5
        kharcha_req = {'line_items': [{
            'item_id': str(first_item.id),
            'quantity': discounted_quantity
            }], 'discount_coupons': [coupon_code]}

        resp = self.client.post(url_for('kharcha'), data=json.dumps(kharcha_req), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])
        resp_json = json.loads(resp.get_data())
        self.assertEqual(resp.status_code, 200)

        base_amount = discounted_quantity * first_item.current_price().amount
        discount_policy = DiscountPolicy.query.filter_by(name=make_name('Unlimited Geek')).one()
        discounted_amount = discounted_quantity * ((discount_policy.percentage / decimal.Decimal('100')) * first_item.current_price().amount)
        self.assertEqual(resp_json.get('line_items')[str(first_item.id)].get('final_amount'),
            base_amount - discounted_amount)

        policy_ids = [str(policy) for policy in resp_json.get('line_items')[str(first_item.id)].get('discount_policy_ids')]
        expected_discount_policy_ids = [discount_policy.id]
        # Test that all the discount policies are returned
        for expected_policy_id in expected_discount_policy_ids:
            self.assertIn(str(expected_policy_id), [policy for policy in policy_ids])

    def test_coupon_limit(self):
        first_item = Item.query.filter_by(name='conference-ticket').first()
        coupon = DiscountCoupon.query.filter_by(code='coupon1').first()
        discounted_quantity = 2
        kharcha_req = {'line_items': [{'item_id': str(first_item.id), 'quantity': discounted_quantity}], 'discount_coupons': [coupon.code]}
        resp = self.client.post(url_for('kharcha'), data=json.dumps(kharcha_req), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])
        self.assertEqual(resp.status_code, 200)
        resp_json = json.loads(resp.get_data())

        base_amount = discounted_quantity * first_item.current_price().amount
        discounted_amount = (coupon.discount_policy.percentage * first_item.current_price().amount) / decimal.Decimal(100.0)
        self.assertEqual(resp_json.get('line_items')[str(first_item.id)].get('final_amount'),
            base_amount - discounted_amount)

        expected_discount_policy_ids = [str(coupon.discount_policy_id)]
        policy_ids = [str(policy) for policy in resp_json.get('line_items')[str(first_item.id)].get('discount_policy_ids')]

        # Test that all the discount policies are returned
        for expected_policy_id in expected_discount_policy_ids:
            self.assertIn(expected_policy_id, [policy for policy in policy_ids])

    def test_discounted_price_kharcha(self):
        first_item = Item.query.filter_by(name='conference-ticket').first()
        coupon = DiscountCoupon.query.filter_by(code='forever').first()
        discounted_quantity = 1
        kharcha_req = {'line_items': [{'item_id': str(first_item.id), 'quantity': discounted_quantity}], 'discount_coupons': [coupon.code]}
        resp = self.client.post(url_for('kharcha'), data=json.dumps(kharcha_req), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])
        self.assertEqual(resp.status_code, 200)
        resp_json = json.loads(resp.get_data())

        discounted_price = [price for price in first_item.prices if price.name == 'forever-early-geek'][0]
        self.assertEqual(resp_json.get('line_items')[str(first_item.id)].get('final_amount'),
            int(discounted_price.amount))
        expected_discount_policy_ids = [str(coupon.discount_policy_id)]
        policy_ids = [str(policy) for policy in resp_json.get('line_items')[str(first_item.id)].get('discount_policy_ids')]

        # Test that all the discount policies are returned
        for expected_policy_id in expected_discount_policy_ids:
            self.assertIn(expected_policy_id, [policy for policy in policy_ids])

    def test_discount_policy_without_price_kharcha(self):
        first_item = Item.query.filter_by(name='conference-ticket').first()
        coupon = DiscountCoupon.query.filter_by(code='noprice').first()
        discounted_quantity = 1
        kharcha_req = {'line_items': [{'item_id': str(first_item.id), 'quantity': discounted_quantity}], 'discount_coupons': [coupon.code]}
        # print first_item.discount_policies.all()
        resp = self.client.post(url_for('kharcha'), data=json.dumps(kharcha_req), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])
        # print resp.status_code
        self.assertEqual(resp.status_code, 200)
        resp_json = json.loads(resp.get_data())

        self.assertEqual(resp_json.get('line_items')[str(first_item.id)].get('discounted_amount'), decimal.Decimal(0))

    def test_zero_discounted_price_kharcha(self):
        first_item = Item.query.filter_by(name='conference-ticket').first()
        coupon = DiscountCoupon.query.filter_by(code='zerodi').first()
        discounted_quantity = 1
        kharcha_req = {'line_items': [{'item_id': str(first_item.id), 'quantity': discounted_quantity}], 'discount_coupons': [coupon.code]}
        resp = self.client.post(url_for('kharcha'), data=json.dumps(kharcha_req), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])
        self.assertEqual(resp.status_code, 200)
        resp_json = json.loads(resp.get_data())
        discounted_price = [price for price in first_item.prices if price.name == 'zero-discount'][0]
        self.assertNotEqual(resp_json.get('line_items')[str(first_item.id)].get('final_amount'),
            int(discounted_price.amount))
        expected_discount_policy_ids = [str(coupon.discount_policy_id)]
        policy_ids = [str(policy) for policy in resp_json.get('line_items')[str(first_item.id)].get('discount_policy_ids')]

        # Test that all the discount policies are returned
        for expected_policy_id in expected_discount_policy_ids:
            self.assertNotIn(expected_policy_id, [policy for policy in policy_ids])

    def test_discounted_complex_kharcha(self):
        first_item = Item.query.filter_by(name='conference-ticket').first()
        discounted_quantity = 9
        coupon2 = DiscountCoupon.query.filter_by(code='coupon2').first()
        coupon3 = DiscountCoupon.query.filter_by(code='coupon3').first()
        kharcha_req = {'line_items': [{'item_id': str(first_item.id), 'quantity': discounted_quantity}], 'discount_coupons': [coupon2.code, coupon3.code]}

        resp = self.client.post(url_for('kharcha'), data=json.dumps(kharcha_req), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])

        self.assertEqual(resp.status_code, 200)
        resp_json = json.loads(resp.get_data())

        base_amount = discounted_quantity * first_item.current_price().amount
        discounted_amount = 2 * first_item.current_price().amount
        self.assertEqual(resp_json.get('line_items')[str(first_item.id)].get('final_amount'),
            base_amount - discounted_amount)

        expected_discount_policy_ids = [str(coupon2.discount_policy_id), str(coupon3.discount_policy_id)]
        policy_ids = [str(policy) for policy in resp_json.get('line_items')[str(first_item.id)].get('discount_policy_ids')]
        # Test that all the discount policies are returned
        for expected_policy_id in expected_discount_policy_ids:
            self.assertIn(expected_policy_id, [policy for policy in policy_ids])

    def tearDown(self):
        db.session.rollback()
        db.drop_all()
        self.ctx.pop()
