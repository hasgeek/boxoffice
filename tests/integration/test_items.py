# -*- coding: utf-8 -*-

import json
import unittest
from datetime import datetime, timedelta

from werkzeug.test import EnvironBuilder
from coaster.utils import utcnow

from boxoffice import app
from boxoffice.models import ORDER_STATUS, Assignee, Item, ItemCollection, Order, db
from tests.fixtures import init_data


class TestOrder(unittest.TestCase):
    def setUp(self):
        self.ctx = app.test_request_context()
        self.ctx.push()
        init_data()
        self.client = app.test_client()
        builder = EnvironBuilder(method='POST')
        self.post_env = builder.get_environ()

    def test_assign(self):
        item = Item.query.filter_by(name='conference-ticket').first()
        item.transferable_until = utcnow() + timedelta(days=2)
        item.event_date = utcnow() + timedelta(days=2)
        db.session.commit()

        data = {
            'line_items': [{'item_id': unicode(item.id), 'quantity': 3}],
            'buyer': {
                'fullname': 'Testing',
                'phone': '9814141414',
                'email': 'test@hasgeek.com',
            },
        }
        ic = ItemCollection.query.first()
        resp = self.client.post(
            '/ic/{ic}/order'.format(ic=ic.id),
            data=json.dumps(data),
            content_type='application/json',
            headers=[
                ('X-Requested-With', 'XMLHttpRequest'),
                ('Origin', app.config['BASE_URL']),
            ],
        )
        self.assertEquals(resp.status_code, 201)
        resp_data = json.loads(resp.data)['result']
        order = Order.query.get(resp_data.get('order_id'))
        self.assertEquals(order.status, ORDER_STATUS.PURCHASE_ORDER)

        self.assertEqual(len(order.line_items), 3)
        li_one = order.line_items[0]
        li_two = order.line_items[1]
        li_three = order.line_items[2]

        # No assingee set yet
        self.assertIsNone(li_one.current_assignee)
        # let's assign one
        data = {
            'line_item_id': str(li_one.id),
            'attendee': {
                'fullname': 'Testing',
                'phone': '9814141414',
                'email': 'test@hasgeek.com',
            },
        }
        resp = self.client.post(
            '/participant/{access_token}/assign'.format(
                access_token=order.access_token
            ),
            data=json.dumps(data),
            content_type='application/json',
            headers=[
                ('X-Requested-With', 'XMLHttpRequest'),
                ('Origin', app.config['BASE_URL']),
            ],
        )
        self.assertEqual(json.loads(resp.data)['status'], 'ok')
        self.assertIsNotNone(li_one.current_assignee)

        # Now assigning the other line item to same email address should fail
        data = {
            'line_item_id': str(li_two.id),
            'attendee': {
                'fullname': 'Testing',
                'phone': '9814141414',
                'email': 'test@hasgeek.com',
            },
        }
        resp = self.client.post(
            '/participant/{access_token}/assign'.format(
                access_token=order.access_token
            ),
            data=json.dumps(data),
            content_type='application/json',
            headers=[
                ('X-Requested-With', 'XMLHttpRequest'),
                ('Origin', app.config['BASE_URL']),
            ],
        )
        self.assertEqual(json.loads(resp.data)['status'], 'error')

        # But reassigning li_one should still work
        data = {
            'line_item_id': str(li_one.id),
            'attendee': {
                'fullname': 'Testing',
                'phone': '9814141414',
                'email': 'test45@hasgeek.com',
            },
        }
        resp = self.client.post(
            '/participant/{access_token}/assign'.format(
                access_token=order.access_token
            ),
            data=json.dumps(data),
            content_type='application/json',
            headers=[
                ('X-Requested-With', 'XMLHttpRequest'),
                ('Origin', app.config['BASE_URL']),
            ],
        )
        self.assertEqual(json.loads(resp.data)['status'], 'ok')

        # let's set transferable_until date to a past date
        item.transferable_until = utcnow() - timedelta(days=2)
        db.session.commit()

        # now another transfer of li_one should fail
        data = {
            'line_item_id': str(li_one.id),
            'attendee': {
                'fullname': 'Testing',
                'phone': '9814141415',
                'email': 'test2@hasgeek.com',
            },
        }
        resp = self.client.post(
            '/participant/{access_token}/assign'.format(
                access_token=order.access_token
            ),
            data=json.dumps(data),
            content_type='application/json',
            headers=[
                ('X-Requested-With', 'XMLHttpRequest'),
                ('Origin', app.config['BASE_URL']),
            ],
        )
        self.assertEqual(json.loads(resp.data)['status'], 'error')

        # li_two still doesn't have an assignee
        self.assertIsNone(li_two.current_assignee)

        # if `item.event_date` is in the past,
        # ticket assign/transfer should not be allowed
        item.event_date = utcnow().date() - timedelta(days=2)
        db.session.commit()

        data = {
            'line_item_id': str(li_two.id),
            'attendee': {
                'fullname': 'Testing',
                'phone': '9814141415',
                'email': 'test234@hasgeek.com',
            },
        }
        resp = self.client.post(
            '/participant/{access_token}/assign'.format(
                access_token=order.access_token
            ),
            data=json.dumps(data),
            content_type='application/json',
            headers=[
                ('X-Requested-With', 'XMLHttpRequest'),
                ('Origin', app.config['BASE_URL']),
            ],
        )
        self.assertEqual(json.loads(resp.data)['status'], 'error')

        # but if `item.event_date` is today or in the future,
        # even if the transfer date is over, we should
        # allow setting a new assignee
        self.assertIsNone(li_three.current_assignee)

        item.event_date = utcnow().date()
        item.transferable_until = utcnow() - timedelta(days=2)
        db.session.commit()

        data = {
            'line_item_id': str(li_three.id),
            'attendee': {
                'fullname': 'Testing',
                'phone': '9814141415',
                'email': 'test234@hasgeek.com',
            },
        }
        resp = self.client.post(
            '/participant/{access_token}/assign'.format(
                access_token=order.access_token
            ),
            data=json.dumps(data),
            content_type='application/json',
            headers=[
                ('X-Requested-With', 'XMLHttpRequest'),
                ('Origin', app.config['BASE_URL']),
            ],
        )
        self.assertEqual(json.loads(resp.data)['status'], 'ok')
