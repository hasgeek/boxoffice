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

        self.assertEquals(resp_json.get('line_items')[0].get('final_amount'), undiscounted_quantity * Price.current(first_item).amount)
        activated_policies = [(policy.get('id'), policy.get('activated')) for policy in resp_json.get('line_items')[0].get('discount_policies')]
        expected_discount_policy_ids = [unicode(policy.id) for policy in first_item.discount_policies]
        self.assertEquals(activated_policies[0], (expected_discount_policy_ids[0], False))

    def test_discounted_kharcha(self):
        first_item = Item.query.first()
        discounted_quantity = 10
        kharcha_req = {'line_items': [{'item_id': unicode(first_item.id), 'quantity': discounted_quantity}]}
        resp = self.client.post(url_for('kharcha'), data=json.dumps(kharcha_req), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest')])
        self.assertEquals(resp.status_code, 200)
        resp_json = json.loads(resp.get_data())

        base_amount = discounted_quantity * Price.current(first_item).amount
        discounted_amount = (first_item.discount_policies[0].percentage * base_amount)/decimal.Decimal(100.0)
        self.assertEquals(resp_json.get('line_items')[0].get('final_amount'), base_amount-discounted_amount)
        expected_discount_policy_ids = [unicode(policy.id) for policy in first_item.discount_policies]
        activated_policies = [(policy.get('id'), policy.get('activated')) for policy in resp_json.get('line_items')[0].get('discount_policies')]
        self.assertEquals(activated_policies[0], (expected_discount_policy_ids[0], True))

    def tearDown(self):
        db.session.rollback()
        db.drop_all()
        self.ctx.pop()
