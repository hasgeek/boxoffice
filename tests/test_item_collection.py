import json
import unittest

from boxoffice import app
from boxoffice.models import ItemCollection, db

from .fixtures import init_data


class TestItemCollectionAPI(unittest.TestCase):

    expected_keys = ['categories', 'html', 'refund_policy']
    expected_categories_names = ['conference', 'workshop', 'merchandise']
    expected_data = {
        "conference": {
            "conference-ticket": {
                "title": "Conference ticket",
                "price": 3500,
                "description": '<p><i class="fa fa-calendar"></i>14 - 15 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>MLR Convention Center, JP Nagar</p><p>This ticket gets you access to rootconf conference on 14th and 15th April 2016.</p>',
                "name": "conference-ticket",
                "quantity_total": 1000,
            },
            "single-day": {
                "title": "Single Day",
                "price": 2500,
                "description": '<p><i class="fa fa-calendar"></i>14 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>MLR Convention Center, JP Nagar</p><p>This ticket gets you access to rootconf conference on 14th April 2016.</p>',
                "name": "single-day",
                "quantity_total": 1000,
            },
        },
        "workshop": {
            "dnssec-workshop": {
                "title": "DNSSEC workshop",
                "price": 2500,
                "description": '<p><i class="fa fa-calendar"></i>12 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>TERI, Domlur</p><p>This ticket gets you access to DNSSEC workshop 12th April 2016.</p>',
                "name": "dnssec-workshop",
                "quantity_total": 1000,
            },
        },
        "merchandise": {
            "t-shirt": {
                "title": "T-shirt",
                "price": 500,
                "description": "Rootconf",
                "name": "t-shirt",
                "quantity_total": 1000,
            },
        },
    }

    def setUp(self):
        self.ctx = app.test_request_context()
        self.ctx.push()
        init_data()
        self.client = app.test_client()
        ic = ItemCollection.query.first()
        self.resp = self.client.get(
            '/ic/{ic}'.format(ic=ic.id),
            headers=[
                ('X-Requested-With', 'XMLHttpRequest'),
                ('Origin', app.config['BASE_URL']),
            ],
        )

    def test_status(self):
        self.assertEqual(self.resp.status_code, 200)

    def test_root_keys(self):
        data = json.loads(self.resp.data)
        self.assertEqual(sorted(data.keys()), sorted(self.expected_keys))

    def test_category_keys(self):
        data = json.loads(self.resp.data)
        self.assertEqual(
            sorted([cat['name'] for cat in data['categories']]),
            sorted(self.expected_categories_names),
        )

        for category in data['categories']:
            expected_items = self.expected_data[category['name']]
            self.assertEqual(
                sorted([c['name'] for c in category['items']]),
                sorted(expected_items.keys()),
            )

            for item in category['items']:
                expected_item_data = expected_items[item['name']]
                self.assertEqual(item['title'], expected_item_data['title'])
                self.assertEqual(item['price'], expected_item_data['price'])
                self.assertEqual(item['description'], expected_item_data['description'])
                self.assertEqual(
                    item['quantity_total'], expected_item_data['quantity_total']
                )

    def tearDown(self):
        db.session.rollback()
        db.drop_all()
        self.ctx.pop()
