import unittest
import json
from boxoffice import app
from boxoffice.models import ItemCollection
from .test_db import TestDatabaseFixture


class TestItemCollectionAPI(TestDatabaseFixture):

    expected_keys = ["categories", "html"]
    expected_categories_names = [u'conference', u'workshop', u'merchandise']
    expected_data = {
        u"conference": {
            u"conference-ticket": {
                "title": "Conference ticket",
                "price": 3500,
                "description": '<p><i class="fa fa-calendar"></i>14 - 15 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>MLR Convention Center, JP Nagar</p><p>This ticket gets you access to rootconf conference on 14th and 15th April 2016.</p>',
                "name": "conference-ticket",
                "quantity_available": 100,
                "quantity_total": 1000,
                },
            u"single-day": {
                u"title": u"Single Day",
                u"price": 2500,
                u"description": u'<p><i class="fa fa-calendar"></i>14 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>MLR Convention Center, JP Nagar</p><p>This ticket gets you access to rootconf conference on 14th April 2016.</p>',
                u"name": u"single-day",
                u"quantity_available": 100,
                u"quantity_total": 1000,
                }
            },
        u"workshop": {
            "dnssec-workshop": {
                u"title": u"DNSSEC workshop",
                u"price": 2500,
                u"description": u'<p><i class="fa fa-calendar"></i>12 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>TERI, Domlur</p><p>This ticket gets you access to DNSSEC workshop 12th April 2016.</p>',
                u"name": u"dnssec-workshop",
                u"quantity_available": 100,
                u"quantity_total": 1000,
                },
            },
        u"merchandise": {
            "t-shirt": {
                "title": "T-shirt",
                "price": 500,
                "description": "Rootconf",
                "name": "t-shirt",
                "quantity_available": 100,
                "quantity_total": 1000,
                },
            },
        }

    def setUp(self):
        """
        setUp that runs after each test method.
        """
        self.app = app
        self.client = app.test_client()
        ic = ItemCollection.query.first()
        self.resp = self.client.get('/ic/{ic}'.format(ic=ic.id), headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])

    def test_status(self):
        self.assertEquals(self.resp.status_code, 200)

    def test_root_keys(self):
        data = json.loads(self.resp.data)
        self.assertEquals(sorted(data.keys()), sorted(self.expected_keys))

    def test_category_keys(self):
        data = json.loads(self.resp.data)
        self.assertEquals(sorted([cat['name'] for cat in data['categories']]), sorted(self.expected_categories_names))
        for category in data['categories']:
            expected_items = self.expected_data[category['name']]
            self.assertEquals(sorted([c['name'] for c in category['items']]), sorted(expected_items.keys()))

            for item in category['items']:
                expected_item_data = expected_items[item['name']]
                self.assertEquals(item['title'], expected_item_data['title'])
                self.assertEquals(item['price'], expected_item_data['price'])
                self.assertEquals(item['description'], expected_item_data['description'])
                self.assertEquals(item['quantity_available'], expected_item_data['quantity_available'])
                self.assertEquals(item['quantity_total'], expected_item_data['quantity_total'])
