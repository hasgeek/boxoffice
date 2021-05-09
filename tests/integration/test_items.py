from datetime import timedelta
import json
import unittest

from werkzeug.test import EnvironBuilder

from boxoffice import app
from boxoffice.models import ORDER_STATUS, Item, ItemCollection, Order, db
from coaster.utils import utcnow
from tests.fixtures import init_data


class TestItems(unittest.TestCase):
    def setUp(self):
        self.ctx = app.test_request_context()
        self.ctx.push()
        init_data()
        self.client = app.test_client()
        builder = EnvironBuilder(method='POST')
        self.post_env = builder.get_environ()

    def ajax_post(self, url, data):
        return self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json',
            headers=[
                ('X-Requested-With', 'XMLHttpRequest'),
                ('Origin', app.config['BASE_URL']),
            ],
        )

    def test_assign(self):
        item = Item.query.filter_by(name="conference-ticket").first()

        data = {
            'line_items': [{'item_id': str(item.id), 'quantity': 2}],
            'buyer': {
                'fullname': 'Testing',
                'phone': '9814141414',
                'email': 'test@hasgeek.com',
            },
        }
        ic = ItemCollection.query.first()
        resp = self.ajax_post('/ic/{ic}/order'.format(ic=ic.id), data)

        self.assertEqual(resp.status_code, 201)
        resp_data = json.loads(resp.data)['result']
        order = Order.query.get(resp_data.get('order_id'))
        self.assertEqual(order.status, ORDER_STATUS.PURCHASE_ORDER)

        self.assertEqual(len(order.line_items), 2)
        li_one = order.line_items[0]
        li_two = order.line_items[1]

        # li_one has no assingee set yet, so it should be possible to set one
        self.assertIsNone(li_one.current_assignee)
        data = {
            'line_item_id': str(li_one.id),
            'attendee': {
                'fullname': 'Testing',
                'phone': '9814141414',
                'email': 'test11@hasgeek.com',
            },
        }
        resp = self.ajax_post(
            '/participant/{access_token}/assign'.format(
                access_token=order.access_token
            ),
            data,
        )
        self.assertEqual(json.loads(resp.data)['status'], 'ok')
        self.assertIsNotNone(li_one.current_assignee)

        # Now assigning the other line item to same email address should fail
        data = {
            'line_item_id': str(li_two.id),
            'attendee': {
                'fullname': 'Testing',
                'phone': '9814141414',
                'email': 'test11@hasgeek.com',
            },
        }
        resp = self.ajax_post(
            '/participant/{access_token}/assign'.format(
                access_token=order.access_token
            ),
            data,
        )
        self.assertEqual(json.loads(resp.data)['status'], 'error')

        # But reassigning li_one should still work
        data = {
            'line_item_id': str(li_one.id),
            'attendee': {
                'fullname': 'Testing',
                'phone': '9814141414',
                'email': 'test12@hasgeek.com',  # email is the measure of uniqueness
            },
        }
        resp = self.ajax_post(
            '/participant/{access_token}/assign'.format(
                access_token=order.access_token
            ),
            data,
        )
        self.assertEqual(json.loads(resp.data)['status'], 'ok')

        # if no transferable_until is set, and no event_date is set,
        # transfer is allowed indefinitely.
        item.transferable_until = None
        item.event_date = None
        db.session.commit()

        self.assertTrue(li_one.is_transferable)

        item.transferable_until = utcnow() + timedelta(days=2)
        item.event_date = utcnow() + timedelta(days=2)
        db.session.commit()

        # let's set transferable_until date to a past date,
        # so now another transfer of li_one should fail
        item.transferable_until = utcnow() - timedelta(days=2)
        db.session.commit()

        data = {
            'line_item_id': str(li_one.id),
            'attendee': {
                'fullname': 'Testing',
                'phone': '9814141415',
                'email': 'test13@hasgeek.com',
            },
        }
        resp = self.ajax_post(
            '/participant/{access_token}/assign'.format(
                access_token=order.access_token
            ),
            data,
        )
        self.assertEqual(json.loads(resp.data)['status'], 'error')

        # li_two still doesn't have an assignee
        self.assertIsNone(li_two.current_assignee)

        # if `item.event_date` is in the past, and
        # `transferable_until` is not set,
        # ticket assign should still be allowed.
        # ticket assign doesn't have a deadline right now.
        item.event_date = utcnow().date() - timedelta(days=2)
        item.transferable_until = None
        db.session.commit()

        data = {
            'line_item_id': str(li_two.id),
            'attendee': {
                'fullname': 'Testing',
                'phone': '9814141415',
                'email': 'test21@hasgeek.com',
            },
        }
        resp = self.ajax_post(
            '/participant/{access_token}/assign'.format(
                access_token=order.access_token
            ),
            data,
        )
        self.assertEqual(json.loads(resp.data)['status'], 'ok')

        # but ticket transfer has a hard deadline in the
        # absense of  'transferable_until' - `event_date`.
        # so, if `transferable_until` is not set and `event_date` is in the past,
        # ticket transfer should fail.
        self.assertIsNotNone(li_two.current_assignee)

        item.event_date = utcnow().date() - timedelta(days=2)
        item.transferable_until = None
        db.session.commit()

        data = {
            'line_item_id': str(li_two.id),
            'attendee': {
                'fullname': 'Testing',
                'phone': '9814141415',
                'email': 'test22@hasgeek.com',
            },
        }
        resp = self.ajax_post(
            '/participant/{access_token}/assign'.format(
                access_token=order.access_token
            ),
            data,
        )
        self.assertEqual(json.loads(resp.data)['status'], 'error')
