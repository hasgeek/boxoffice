import unittest
import json
from boxoffice import app, init_for
from boxoffice.models import *
from fixtures import init_data


class TestOrder(unittest.TestCase):

    expected_keys = ["categories", "html"]
    expected_categories_names = ['conference', 'workshop', 'merchandise']
    expected_data = {
        "conference": {
            "conference-ticket": {
                "title": "Conference ticket",
                "price": 3500,
                "description": '<p><i class="fa fa-calendar"></i>14 - 15 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>MLR Convention Center, JP Nagar</p><p>This ticket gets you access to rootconf conference on 14th and 15th April 2016.</p>',
                "name": "conference-ticket",
                "quantity_available": 100,
                "quantity_total": 1000,
                },
            "single-day": {
                "title": "Single Day",
                "price": 2500,
                "description": '<p><i class="fa fa-calendar"></i>14 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>MLR Convention Center, JP Nagar</p><p>This ticket gets you access to rootconf conference on 14th April 2016.</p>',
                "name": "single-day",
                "quantity_available": 100,
                "quantity_total": 1000,
                }
            },
        "workshop": {
            "dnssec-workshop": {
                "title": "DNSSEC workshop",
                "price": 2500,
                "description": '<p><i class="fa fa-calendar"></i>12 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>TERI, Domlur</p><p>This ticket gets you access to DNSSEC workshop 12th April 2016.</p>',
                "name": "dnssec-workshop",
                "quantity_available": 100,
                "quantity_total": 1000,
                },
            },
        "merchandise": {
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
        self.ctx = app.test_request_context()
        self.ctx.push()
        init_for('test')
        db.create_all()
        init_data()
        self.client = app.test_client()

    def test_basic(self):
        item = Item.query.first()
        data = {
            'line_items': [{'item_id': unicode(item.id), 'quantity': 2}],
            'email': 'test@hasgeek.com'
            }
        resp = self.client.post('/rootconf/2016/order', data=json.dumps(data), content_type='application/x-www-form-urlencoded')
        data = json.loads(resp.data)
        self.assertEquals(data['code'], 200)
        self.assertEquals(data['final_amount'], 7000)

    # def test_invalid_item(self):
    #     data = {
    #         'line_items': [{'item_id': 'uuidtdoesntexist', 'quantity': 2}],
    #         'email': 'test@hasgeek.com'
    #         }
    #     resp = self.client.post('/rootconf/2016/order', data=json.dumps(data), content_type='application/x-www-form-urlencoded')
    #     data = json.loads(resp.data)
    #     print data
    #     self.assertEquals(data['code'], 200)
    #     self.assertEquals(data['final_amount'], 7000)

    def test_simple_discounted_item(self):
        discounted_item = Item.query.filter_by(name='t-shirt').first()
        data = {
            'line_items': [{'item_id': unicode(discounted_item.id), 'quantity': 5}],
            'email': 'test@hasgeek.com'
            }
        resp = self.client.post('/rootconf/2016/order', data=json.dumps(data), content_type='application/x-www-form-urlencoded')
        data = json.loads(resp.data)
        self.assertEquals(data['code'], 200)
        self.assertEquals(data['final_amount'], 2375)

    def test_complex_discounted_item(self):
        discounted_item1 = Item.query.filter_by(name='t-shirt').first()
        discounted_item2 = Item.query.filter_by(name='conference-ticket').first()
        data = {
            'line_items': [{
                    'item_id': unicode(discounted_item1.id),
                    'quantity': 5
                    },
                    {
                    'item_id': unicode(discounted_item2.id),
                    'quantity': 10
                    }
                ],
            'email': 'test@hasgeek.com'
            }
        resp = self.client.post('/rootconf/2016/order', data=json.dumps(data), content_type='application/x-www-form-urlencoded')
        data = json.loads(resp.data)
        self.assertEquals(data['code'], 200)
        # 10*3500@90% + 5*500*@95 = 33875
        self.assertEquals(data['final_amount'], 33875)

    def tearDown(self):
        db.session.rollback()
        db.drop_all()
        self.ctx.pop()
