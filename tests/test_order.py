import unittest
import json
import decimal
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
                'phone': '9814141414',
                'email': 'test@hasgeek.com',
                }
            }
        ic = ItemCollection.query.first()
        resp = self.client.post('/ic/{ic}/order'.format(ic=ic.id), data=json.dumps(data), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])
        data = json.loads(resp.data)
        self.assertEquals(resp.status_code, 201)
        order = Order.query.get(data.get('order_id'))
        self.assertEquals(order.status, ORDER_STATUS.PURCHASE_ORDER)
        # 3500*2 = 7000
        self.assertEquals(data['final_amount'], 7000)

    def test_simple_discounted_item(self):
        discounted_item = Item.query.filter_by(name='t-shirt').first()
        data = {
            'line_items': [{'item_id': unicode(discounted_item.id), 'quantity': 5}],
            'buyer': {
                'fullname': 'Testing',
                'phone': '9814141414',
                'email': 'test@hasgeek.com',
                }
            }
        ic = ItemCollection.query.first()
        resp = self.client.post('/ic/{ic}/order'.format(ic=ic.id), data=json.dumps(data), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])
        data = json.loads(resp.data)

        self.assertEquals(resp.status_code, 201)
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
                'phone': '9814141414',
                'email': 'test@hasgeek.com',
                }
            }
        ic = ItemCollection.query.first()
        resp = self.client.post('/ic/{ic}/order'.format(ic=ic.id), data=json.dumps(data), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])
        data = json.loads(resp.data)
        self.assertEquals(resp.status_code, 201)
        # 10*3500@90% + 5*500*@95 = 33875
        self.assertEquals(data['final_amount'], 33875)

    def test_discounted_complex_order(self):
        conf = Item.query.filter_by(name='conference-ticket').first()
        tshirt = Item.query.filter_by(name='t-shirt').first()
        conf_price = conf.current_price().amount
        tshirt_price = tshirt.current_price().amount
        conf_quantity = 12
        tshirt_quantity = 5
        coupon2 = DiscountCoupon.query.filter_by(code='coupon2').first()
        coupon2_initial_qty = coupon2.quantity_available
        coupon3 = DiscountCoupon.query.filter_by(code='coupon3').first()
        coupon3_initial_qty = coupon3.quantity_available
        data = {
            'line_items': [{
                    'item_id': unicode(tshirt.id),
                    'quantity': tshirt_quantity
                    },
                    {
                    'item_id': unicode(conf.id),
                    'quantity': conf_quantity
                    }
                ],
            'discount_coupons': [coupon2.code, coupon3.code],
            'buyer': {
                'fullname': 'Testing',
                'phone': '9814141414',
                'email': 'test@hasgeek.com',
                }
            }
        ic = ItemCollection.query.first()
        resp = self.client.post('/ic/{ic}/order'.format(ic=ic.id), data=json.dumps(data), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])
        data = json.loads(resp.data)
        self.assertEquals(resp.status_code, 201)
        resp_json = json.loads(resp.get_data())
        order = Order.query.get(resp_json.get('order_id'))
        tshirt_policy = DiscountPolicy.query.filter_by(title='5% discount on 5 t-shirts').first()
        tshirt_final_amount = (tshirt_price * tshirt_quantity) - (tshirt_quantity * (tshirt_policy.percentage * tshirt_price)/decimal.Decimal(100))
        conf_policy = DiscountPolicy.query.filter_by(title='10% discount on rootconf').first()
        conf_final_amount = (conf_price * (conf_quantity-2)) - ((conf_quantity-2) * (conf_policy.percentage * conf_price)/decimal.Decimal(100))
        self.assertEquals(tshirt_final_amount+conf_final_amount, order.get_amounts().final_amount)
        self.assertEquals(coupon2.quantity_available, coupon2_initial_qty)
        self.assertEquals(coupon3.quantity_available, coupon3_initial_qty)

    def tearDown(self):
        db.session.rollback()
        db.drop_all()
        self.ctx.pop()
