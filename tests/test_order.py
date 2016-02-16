import unittest
import json
from boxoffice import app, init_for
from boxoffice.models import *
from fixtures import init_data


class TestOrder(unittest.TestCase):

    def setUp(self):
        self.ctx = app.test_request_context()
        self.ctx.push()
        init_for('test')
        db.create_all()
        init_data()
        self.client = app.test_client()

    def test_basic(self):
        item = Item.query.filter_by(name='conference-ticket').first()
        data = {
            'line_items': [{'item_id': unicode(item.id), 'quantity': 2}],
            'buyer': {
                'fullname': 'Testing',
                'phone': 9814141414,
                'email': 'test@hasgeek.com',
                }
            }
        resp = self.client.post('/rootconf/2016/order', data=json.dumps(data), content_type='application/x-www-form-urlencoded')
        data = json.loads(resp.data)
        self.assertEquals(data['code'], 200)
        # 3500*2 = 7000
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
            'buyer': {
                'fullname': 'Testing',
                'phone': 9814141414,
                'email': 'test@hasgeek.com',
                }
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
            'buyer': {
                'fullname': 'Testing',
                'phone': 9814141414,
                'email': 'test@hasgeek.com',
                }

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
