import decimal
import json
import unittest
from flask import url_for
from boxoffice import app, init_for
from boxoffice.models import (db)
from fixtures import init_data
from boxoffice.models import Price, Item

SERVER_NAME = 'http://shreyas-wlan.dev:6500'


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
        first_item = Item.query.first()
        undiscounted_quantity = 2
        kharcha_req = {'line_items': [{'item_id': unicode(first_item.id), 'quantity': undiscounted_quantity}]}
        resp = self.client.post(url_for('kharcha'), data=json.dumps(kharcha_req), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest')])

        self.assertEquals(resp.status_code, 200)
        resp_json = json.loads(resp.get_data())
        # Test that the price is correct
        self.assertEquals(resp_json.get('line_items')[0].get('final_amount'),
            undiscounted_quantity * Price.current(first_item).amount)

        policies = [(unicode(policy.get('id')), policy.get('activated'))
            for policy in resp_json.get('line_items')[0].get('discount_policies')]
        self.assertEquals(resp_json.get('line_items')[0].get('final_amount'), undiscounted_quantity * Price.current(first_item).amount)
        expected_discount_policy_ids = [unicode(policy.id) for policy in first_item.discount_policies]

        # Test that all the discount policies are returned
        for expected_policy_id in expected_discount_policy_ids:
            self.assertIn(expected_policy_id, [policy[0] for policy in policies])

        # Test that none of the item's discounted policies are activated
        for policy in policies:
            self.assertFalse(policy[1])

    def test_discounted_kharcha(self):
        first_item = Item.query.first()
        discounted_quantity = 10
        kharcha_req = {'line_items': [{'item_id': unicode(first_item.id), 'quantity': discounted_quantity}]}
        resp = self.client.post(url_for('kharcha'), data=json.dumps(kharcha_req), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest')])
        self.assertEquals(resp.status_code, 200)
        resp_json = json.loads(resp.get_data())

        base_amount = discounted_quantity * Price.current(first_item).amount
        discounted_amount = (first_item.discount_policies[0].percentage * base_amount)/decimal.Decimal(100.0)
        self.assertEquals(resp_json.get('line_items')[0].get('final_amount'),
            base_amount-discounted_amount)

        expected_discount_policy_ids = [unicode(policy.id) for policy in first_item.discount_policies]
        policies = [(unicode(policy.get('id')), policy.get('activated')) for policy in resp_json.get('line_items')[0].get('discount_policies')]

        # Test that all the discount policies are returned
        for expected_policy_id in expected_discount_policy_ids:
            self.assertIn(expected_policy_id, [policy[0] for policy in policies])

        # Test that the item's discounted policies are activated
        for policy in policies:
            self.assertTrue(policy[1])

    def tearDown(self):
        db.session.rollback()
        db.drop_all()
        self.ctx.pop()
