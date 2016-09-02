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

    def test_order_with_invalid_quantity(self):
        item = Item.query.filter_by(name='conference-ticket').first()
        data = {
            'line_items': [{'item_id': unicode(item.id), 'quantity': 1001}],
            'buyer': {
                'fullname': 'Testing',
                'phone': '9814141414',
                'email': 'test@hasgeek.com',
                }
            }
        ic = ItemCollection.query.first()
        resp = self.client.post('/ic/{ic}/order'.format(ic=ic.id), data=json.dumps(data), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])
        self.assertEquals(resp.status_code, 400)

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

    def test_expired_item_order(self):
        expired_ticket = Item.query.filter_by(name='expired-ticket').first()
        quantity = 2
        data = {
            'line_items': [{'item_id': unicode(expired_ticket.id), 'quantity': quantity}],
            'buyer': {
                'fullname': 'Testing',
                'phone': '9814141414',
                'email': 'test@hasgeek.com',
                }
            }
        ic = ItemCollection.query.first()
        resp = self.client.post('/ic/{ic}/order'.format(ic=ic.id), data=json.dumps(data), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])
        self.assertEquals(resp.status_code, 400)

    def test_signed_discounted_coupon_order(self):
        first_item = Item.query.filter_by(name='conference-ticket').first()
        signed_policy = DiscountPolicy.query.filter_by(name='signed').first()
        signed_code = signed_policy.gen_signed_code()
        discounted_quantity = 1
        data = {
            'line_items': [{'item_id': unicode(first_item.id), 'quantity': discounted_quantity}],
            'discount_coupons': [signed_code],
            'buyer': {
                'fullname': 'Testing',
                'phone': '9814141414',
                'email': 'test@hasgeek.com',
                }
            }
        ic = ItemCollection.query.first()
        resp = self.client.post('/ic/{ic}/order'.format(ic=ic.id), data=json.dumps(data), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])
        resp_data = json.loads(resp.data)
        self.assertEquals(resp.status_code, 201)
        self.assertEquals(resp_data['final_amount'], first_item.current_price().amount - (signed_policy.percentage*first_item.current_price().amount)/decimal.Decimal(100.0))
        line_item = LineItem.query.filter_by(customer_order_id=resp_data['order_id']).first()
        self.assertEquals(line_item.discount_coupon.code, signed_code)

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
        coupon3 = DiscountCoupon.query.filter_by(code='coupon3').first()
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

    def test_free_order(self):
        item = Item.query.filter_by(name='conference-ticket').first()
        data = {
            'line_items': [{'item_id': unicode(item.id), 'quantity': 1}],
            'buyer': {
                'fullname': 'Testing',
                'phone': '9814141414',
                'email': 'test@hasgeek.com',
                },
            'discount_coupons': ['coupon2']
            }
        ic = ItemCollection.query.first()
        resp = self.client.post('/ic/{ic}/order'.format(ic=ic.id), data=json.dumps(data), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])
        data = json.loads(resp.data)
        self.assertEquals(resp.status_code, 201)
        order = Order.query.get(data.get('order_id'))
        self.assertEquals(order.status, ORDER_STATUS.PURCHASE_ORDER)
        self.assertEquals(order.line_items[0].status, LINE_ITEM_STATUS.PURCHASE_ORDER)
        self.assertEquals(data['final_amount'], 0)
        resp = self.client.post('/order/{order_id}/free'.format(order_id=order.id), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])
        self.assertEquals(resp.status_code, 201)
        coupon = DiscountCoupon.query.filter_by(code='coupon2').first()
        self.assertEquals(coupon.used_count, 1)
        self.assertEquals(order.status, ORDER_STATUS.SALES_ORDER)
        self.assertEquals(order.line_items[0].status, LINE_ITEM_STATUS.CONFIRMED)

    def tearDown(self):
        db.session.rollback()
        db.drop_all()
        self.ctx.pop()
