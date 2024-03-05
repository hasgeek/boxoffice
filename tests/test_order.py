from unittest.mock import patch
from uuid import UUID
import datetime
import decimal
import json

import pytest

from coaster.utils import buid

from boxoffice import app
from boxoffice.forms import OrderRefundForm
from boxoffice.models import (
    CurrencyEnum,
    DiscountCoupon,
    DiscountPolicy,
    Item,
    ItemCollection,
    LineItem,
    LineItemStatus,
    OnlinePayment,
    Order,
    OrderStatus,
    PaymentTransaction,
)
from boxoffice.models.payment import TransactionTypeEnum
from boxoffice.views.custom_exceptions import PaymentGatewayError
from boxoffice.views.order import (
    process_line_item_cancellation,
    process_partial_refund_for_order,
)


class MockResponse:
    def __init__(self, response_data, status_code=200):
        self.response_data = response_data
        self.status_code = status_code

    def json(self):
        return self.response_data


def test_basic(client, all_data) -> None:
    ticket = Item.query.filter_by(name='conference-ticket').one()
    data = {
        'line_items': [{'ticket_id': str(ticket.id), 'quantity': 2}],
        'buyer': {
            'fullname': 'Testing',
            'phone': '9814141414',
            'email': 'test@hasgeek.com',
        },
    }
    menu = ItemCollection.query.one()
    resp = client.post(
        f'/menu/{menu.id}/order',
        data=json.dumps(data),
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )
    assert resp.status_code == 201
    resp_data = json.loads(resp.data)['result']
    order = Order.query.get(resp_data.get('order_id'))
    assert isinstance(order, Order)
    assert order.status == OrderStatus.PURCHASE_ORDER
    # 3500*2 = 7000
    assert resp_data['final_amount'] == 7000


def test_basic_with_utm_headers(client, all_data) -> None:
    ticket = Item.query.filter_by(name='conference-ticket').one()
    utm_campaign = 'campaign'
    utm_medium = 'medium'
    utm_source = 'source'
    utm_term = 'term'
    utm_content = 'content'
    utm_id = 'id'
    gclid = 'gclid'
    data = {
        'line_items': [{'ticket_id': str(ticket.id), 'quantity': 2}],
        'buyer': {
            'fullname': 'Testing',
            'phone': '9814141414',
            'email': 'test@hasgeek.com',
        },
        'order_session': {
            'utm_campaign': utm_campaign,
            'utm_medium': utm_medium,
            'utm_source': utm_source,
            'utm_term': utm_term,
            'utm_content': utm_content,
            'utm_id': utm_id,
            'gclid': gclid,
        },
    }
    menu = ItemCollection.query.one()
    resp = client.post(
        f'/menu/{menu.id}/order',
        data=json.dumps(data),
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )
    assert resp.status_code == 201
    resp_data = json.loads(resp.data)['result']
    order = Order.query.get(resp_data.get('order_id'))
    assert isinstance(order, Order)
    order_session = order.session
    assert order_session.utm_campaign == utm_campaign
    assert order_session.utm_medium == utm_medium
    assert order_session.utm_source == utm_source
    assert order_session.utm_term == utm_term
    assert order_session.utm_content == utm_content
    assert order_session.utm_id == utm_id
    assert order_session.gclid == gclid


def test_order_with_invalid_quantity(client, all_data) -> None:
    ticket = Item.query.filter_by(name='conference-ticket').one()
    data = {
        'line_items': [{'ticket_id': str(ticket.id), 'quantity': 1001}],
        'buyer': {
            'fullname': 'Testing',
            'phone': '9814141414',
            'email': 'test@hasgeek.com',
        },
    }
    menu = ItemCollection.query.one()
    resp = client.post(
        f'/menu/{menu.id}/order',
        data=json.dumps(data),
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )
    assert resp.status_code == 400


def test_simple_discounted_item(client, all_data) -> None:
    discounted_item = Item.query.filter_by(name='t-shirt').one()
    data = {
        'line_items': [{'ticket_id': str(discounted_item.id), 'quantity': 5}],
        'buyer': {
            'fullname': 'Testing',
            'phone': '9814141414',
            'email': 'test@hasgeek.com',
        },
    }
    menu = ItemCollection.query.one()
    resp = client.post(
        f'/menu/{menu.id}/order',
        data=json.dumps(data),
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )
    assert resp.status_code == 201
    resp_data = json.loads(resp.data)['result']
    assert resp_data['final_amount'] == 2375


def test_expired_ticket_order(client, all_data) -> None:
    expired_ticket = Item.query.filter_by(name='expired-ticket').one()
    quantity = 2
    data = {
        'line_items': [{'ticket_id': str(expired_ticket.id), 'quantity': quantity}],
        'buyer': {
            'fullname': 'Testing',
            'phone': '9814141414',
            'email': 'test@hasgeek.com',
        },
    }
    menu = ItemCollection.query.one()
    resp = client.post(
        f'/menu/{menu.id}/order',
        data=json.dumps(data),
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )
    assert resp.status_code == 400


def test_signed_discounted_coupon_order(client, all_data) -> None:
    first_item = Item.query.filter_by(name='conference-ticket').one()
    signed_policy = DiscountPolicy.query.filter_by(name='signed').one()
    signed_code = signed_policy.gen_signed_code()
    discounted_quantity = 1
    data = {
        'line_items': [
            {'ticket_id': str(first_item.id), 'quantity': discounted_quantity}
        ],
        'discount_coupons': [signed_code],
        'buyer': {
            'fullname': 'Testing',
            'phone': '9814141414',
            'email': 'test@hasgeek.com',
        },
    }
    menu = ItemCollection.query.one()
    resp = client.post(
        f'/menu/{menu.id}/order',
        data=json.dumps(data),
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )
    assert resp.status_code == 201
    resp_data = json.loads(resp.data)['result']
    current_price = first_item.current_price()
    assert current_price is not None
    assert signed_policy.percentage is not None
    assert resp_data['final_amount'] == current_price.amount - (
        signed_policy.percentage * current_price.amount
    ) / decimal.Decimal(100.0)
    line_item = LineItem.query.filter_by(
        customer_order_id=UUID(hex=resp_data['order_id'])
    ).one()
    assert line_item.discount_coupon is not None
    assert line_item.discount_coupon.code == signed_code


def test_complex_discounted_item(client, all_data) -> None:
    discounted_item1 = Item.query.filter_by(name='t-shirt').one()
    discounted_item2 = Item.query.filter_by(name='conference-ticket').one()
    data = {
        'line_items': [
            {'ticket_id': str(discounted_item1.id), 'quantity': 5},
            {'ticket_id': str(discounted_item2.id), 'quantity': 10},
        ],
        'buyer': {
            'fullname': 'Testing',
            'phone': '9814141414',
            'email': 'test@hasgeek.com',
        },
    }
    menu = ItemCollection.query.one()
    resp = client.post(
        f'/menu/{menu.id}/order',
        data=json.dumps(data),
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )
    assert resp.status_code == 201
    # 10*3500@90% + 5*500*@95 = 33875
    resp_data = json.loads(resp.data)['result']
    assert resp_data['final_amount'] == 33875


def test_discounted_complex_order(client, all_data) -> None:
    conf = Item.query.filter_by(name='conference-ticket').one()
    tshirt = Item.query.filter_by(name='t-shirt').one()
    conf_current_price = conf.current_price()
    assert conf_current_price is not None
    tshirt_current_price = tshirt.current_price()
    assert tshirt_current_price is not None

    conf_price = conf_current_price.amount
    tshirt_price = tshirt_current_price.amount
    conf_quantity = 12
    tshirt_quantity = 5
    coupon2 = DiscountCoupon.query.filter_by(code='coupon2').one()
    coupon3 = DiscountCoupon.query.filter_by(code='coupon3').one()
    data = {
        'line_items': [
            {'ticket_id': str(tshirt.id), 'quantity': tshirt_quantity},
            {'ticket_id': str(conf.id), 'quantity': conf_quantity},
        ],
        'discount_coupons': [coupon2.code, coupon3.code],
        'buyer': {
            'fullname': 'Testing',
            'phone': '9814141414',
            'email': 'test@hasgeek.com',
        },
    }
    menu = ItemCollection.query.one()
    resp = client.post(
        f'/menu/{menu.id}/order',
        data=json.dumps(data),
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )
    assert resp.status_code == 201
    resp_json = json.loads(resp.data)['result']
    order = Order.query.get(resp_json.get('order_id'))
    assert isinstance(order, Order)
    tshirt_policy = DiscountPolicy.query.filter_by(
        title='5% discount on 5 t-shirts'
    ).one()
    assert tshirt_policy.percentage is not None
    tshirt_final_amount = (tshirt_price * tshirt_quantity) - (
        tshirt_quantity
        * (tshirt_policy.percentage * tshirt_price)
        / decimal.Decimal(100)
    )
    conf_policy = DiscountPolicy.query.filter_by(title='10% discount on rootconf').one()
    assert conf_policy.percentage is not None
    conf_final_amount = (conf_price * (conf_quantity - 2)) - (
        (conf_quantity - 2)
        * (conf_policy.percentage * conf_price)
        / decimal.Decimal(100)
    )
    assert (
        tshirt_final_amount + conf_final_amount
        == order.get_amounts(LineItemStatus.PURCHASE_ORDER).final_amount
    )


def make_free_order(client):
    ticket = Item.query.filter_by(name='conference-ticket').one()
    data = {
        'line_items': [{'ticket_id': str(ticket.id), 'quantity': 1}],
        'buyer': {
            'fullname': 'Testing',
            'phone': '9814141414',
            'email': 'test@hasgeek.com',
        },
        'discount_coupons': ['coupon2'],
    }
    menu = ItemCollection.query.one()
    resp = client.post(
        f'/menu/{menu.id}/order',
        data=json.dumps(data),
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )
    return resp


def test_free_order(client, all_data) -> None:
    resp = make_free_order(client)
    assert resp.status_code == 201
    resp_json = json.loads(resp.data)['result']
    order = Order.query.get(resp_json.get('order_id'))
    assert isinstance(order, Order)
    assert order.status == OrderStatus.PURCHASE_ORDER
    assert order.line_items[0].status == LineItemStatus.PURCHASE_ORDER
    assert resp_json['final_amount'] == 0
    resp = client.post(
        f'/order/{order.id}/free',
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )
    assert resp.status_code == 201
    coupon = DiscountCoupon.query.filter_by(code='coupon2').one()
    assert coupon.used_count == 1
    assert order.status == OrderStatus.SALES_ORDER
    assert order.line_items[0].status == (  # type: ignore[unreachable]
        LineItemStatus.CONFIRMED
    )


def test_cancel_line_item_in_order(db_session, client, all_data, post_env) -> None:
    original_quantity = 2
    order_item = Item.query.filter_by(name='t-shirt').one()
    current_price = order_item.current_price()
    assert current_price is not None
    total_amount = current_price.amount * original_quantity
    data = {
        'line_items': [
            {'ticket_id': str(order_item.id), 'quantity': original_quantity}
        ],
        'buyer': {
            'fullname': 'Testing',
            'phone': '9814141414',
            'email': 'test@hasgeek.com',
        },
    }
    menu = ItemCollection.query.one()
    # make a purchase order
    resp = client.post(
        f'/menu/{menu.id}/order',
        data=json.dumps(data),
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )
    assert resp.status_code == 201
    resp_json = json.loads(resp.data)['result']
    assert resp_json['final_amount'] == total_amount

    order = Order.query.get(resp_json['order_id'])
    assert isinstance(order, Order)
    # Create fake payment and transaction objects
    online_payment = OnlinePayment(pg_paymentid='pg_testpayment', order=order)
    online_payment.confirm()
    order_amounts = order.get_amounts(LineItemStatus.PURCHASE_ORDER)
    transaction = PaymentTransaction(
        order=order,
        online_payment=online_payment,
        amount=order_amounts.final_amount,
        currency=CurrencyEnum.INR,
    )
    db_session.add(transaction)
    order.confirm_sale()
    db_session.commit()

    refund_amount = total_amount - 1
    pre_refund_transactions_count = order.refund_transactions.count()
    formdata = {
        'amount': refund_amount,
        'internal_note': 'internal reference',
        'refund_description': 'receipt description',
        'note_to_user': 'price has been halved',
    }
    refund_form = OrderRefundForm(data=formdata, parent=order, meta={'csrf': False})
    partial_refund_args = {
        'order': order,
        'form': refund_form,
        'request_method': 'POST',
    }
    with patch('boxoffice.extapi.razorpay.refund_payment') as mock:
        mock.return_value = MockResponse(response_data={'id': buid()})
        with app.request_context(post_env):
            process_partial_refund_for_order(partial_refund_args)
    assert pre_refund_transactions_count + 1 == order.refund_transactions.count()

    first_line_item = order.line_items[0]
    with patch('boxoffice.extapi.razorpay.refund_payment') as mock:
        mock.return_value = MockResponse(response_data={'id': buid()})
        process_line_item_cancellation(first_line_item)
    assert first_line_item.status == LineItemStatus.CANCELLED
    expected_refund_amount = total_amount - refund_amount
    refund_transaction1 = (
        PaymentTransaction.query.filter_by(
            order=order, transaction_type=TransactionTypeEnum.REFUND
        )
        .order_by(PaymentTransaction.created_at.desc())
        .first()
    )
    assert refund_transaction1 is not None
    assert refund_transaction1.amount == expected_refund_amount


def test_cancel_line_item_in_bulk_order(db_session, client, all_data, post_env) -> None:
    original_quantity = 5
    discounted_item = Item.query.filter_by(name='t-shirt').one()
    current_price = discounted_item.current_price()
    assert current_price is not None
    total_amount = current_price.amount * original_quantity
    data = {
        'line_items': [
            {'ticket_id': str(discounted_item.id), 'quantity': original_quantity}
        ],
        'buyer': {
            'fullname': 'Testing',
            'phone': '9814141414',
            'email': 'test@hasgeek.com',
        },
    }
    menu = ItemCollection.query.one()
    # make a purchase order
    resp = client.post(
        f'/menu/{menu.id}/order',
        data=json.dumps(data),
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )
    assert resp.status_code == 201
    resp_json = json.loads(resp.data)['result']
    assert resp_json['final_amount'] == (
        total_amount - 5 * total_amount / decimal.Decimal(100)
    )

    order = Order.query.get(resp_json['order_id'])
    assert isinstance(order, Order)
    # Create fake payment and transaction objects
    online_payment = OnlinePayment(pg_paymentid='pg_testpayment', order=order)
    online_payment.confirm()
    order_amounts = order.get_amounts(LineItemStatus.PURCHASE_ORDER)
    transaction = PaymentTransaction(
        order=order,
        online_payment=online_payment,
        amount=order_amounts.final_amount,
        currency=CurrencyEnum.INR,
    )
    db_session.add(transaction)
    order.confirm_sale()
    db_session.commit()

    first_line_item = order.line_items[0]
    to_be_void_line_items = order.line_items[1:]
    precancellation_order_amount = order.net_amount

    with patch('boxoffice.extapi.razorpay.refund_payment') as mock:
        mock.return_value = MockResponse(response_data={'id': buid()})
        process_line_item_cancellation(first_line_item)
    assert first_line_item.status == LineItemStatus.CANCELLED
    for void_line_item in to_be_void_line_items:
        assert void_line_item.status == LineItemStatus.VOID
    expected_refund_amount = (
        precancellation_order_amount
        - order.get_amounts(LineItemStatus.CONFIRMED).final_amount
    )
    refund_transaction1 = PaymentTransaction.query.filter_by(
        order=order, transaction_type=TransactionTypeEnum.REFUND
    ).one()
    assert refund_transaction1.amount == expected_refund_amount

    second_line_item = order.confirmed_line_items[0]
    assert isinstance(second_line_item, LineItem)
    with patch('boxoffice.extapi.razorpay.refund_payment') as mock:
        mock.return_value = MockResponse(response_data={'id': buid()})
        process_line_item_cancellation(second_line_item)
    assert second_line_item.status == LineItemStatus.CANCELLED
    refund_transaction2 = (
        PaymentTransaction.query.filter_by(
            order=order, transaction_type=TransactionTypeEnum.REFUND
        )
        .order_by(PaymentTransaction.created_at.desc())
        .first()
    )
    assert refund_transaction2 is not None
    assert refund_transaction2.amount == second_line_item.final_amount

    # test failed cancellation
    third_line_item = order.confirmed_line_items[0]
    with patch('boxoffice.extapi.razorpay.refund_payment') as mock:
        mock.return_value = MockResponse(
            response_data={
                'error': {
                    'code': 'BAD_REQUEST_ERROR',
                    'description': "The amount is invalid",
                    'field': 'amount',
                }
            },
            status_code=400,
        )
        with pytest.raises(PaymentGatewayError):
            process_line_item_cancellation(third_line_item)

    # refund the remaining amount paid, and attempt to cancel a line item
    # this should cancel the line item without resulting in a new refund transaction
    refund_amount = order.net_amount
    refund_dict = {
        'id': buid(),
        'amount': refund_amount,
        'internal_note': 'internal reference',
        'note_to_user': 'you get a refund!',
    }
    formdata = {
        'amount': refund_amount,
        'internal_note': 'internal reference',
        'refund_description': 'receipt description',
        'note_to_user': 'price has been halved',
    }
    refund_form = OrderRefundForm(data=formdata, parent=order, meta={'csrf': False})
    partial_refund_args = {
        'order': order,
        'form': refund_form,
        'request_method': 'POST',
    }
    with patch('boxoffice.extapi.razorpay.refund_payment') as mock:
        mock.return_value = MockResponse(response_data=refund_dict)
        with app.request_context(post_env):
            process_partial_refund_for_order(partial_refund_args)

    third_line_item = order.confirmed_line_items[0]
    pre_cancellation_transactions_count = order.refund_transactions.count()
    cancelled_refund_amount = process_line_item_cancellation(third_line_item)
    assert cancelled_refund_amount == decimal.Decimal(0)
    assert pre_cancellation_transactions_count == order.refund_transactions.count()

    # test free line item cancellation
    free_order_resp = make_free_order(client)
    free_order_resp_data = json.loads(free_order_resp.data)['result']
    free_order = Order.query.get(free_order_resp_data.get('order_id'))
    assert free_order is not None
    free_line_item = free_order.line_items[0]
    process_line_item_cancellation(free_line_item)
    assert free_line_item.status == LineItemStatus.CANCELLED
    assert free_order.transactions.count() == 0


def test_partial_refund_in_order(db_session, client, all_data, post_env) -> None:
    original_quantity = 5
    discounted_item = Item.query.filter_by(name='t-shirt').one()
    current_price = discounted_item.current_price()
    assert current_price is not None
    total_amount = current_price.amount * original_quantity
    data = {
        'line_items': [
            {'ticket_id': str(discounted_item.id), 'quantity': original_quantity}
        ],
        'buyer': {
            'fullname': 'Testing',
            'phone': '9814141414',
            'email': 'test@hasgeek.com',
        },
    }
    menu = ItemCollection.query.one()
    # make a purchase order
    resp = client.post(
        f'/menu/{menu.id}/order',
        data=json.dumps(data),
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )
    assert resp.status_code == 201
    resp_data = json.loads(resp.data)['result']
    assert resp_data['final_amount'] == (
        total_amount - 5 * total_amount / decimal.Decimal(100)
    )

    order = Order.query.get(resp_data['order_id'])
    assert isinstance(order, Order)
    # Create fake payment and transaction objects
    online_payment = OnlinePayment(pg_paymentid='pg_testpayment', order=order)
    online_payment.confirm()
    order_amounts = order.get_amounts(LineItemStatus.PURCHASE_ORDER)
    transaction = PaymentTransaction(
        order=order,
        online_payment=online_payment,
        amount=order_amounts.final_amount,
        currency=CurrencyEnum.INR,
    )
    db_session.add(transaction)
    order.confirm_sale()
    db_session.commit()

    valid_refund_amount = 500

    formdata = {
        'amount': valid_refund_amount,
        'internal_note': 'internal reference',
        'note_to_user': 'you get a refund!',
        'refund_description': 'test refund',
    }
    refund_form = OrderRefundForm(data=formdata, parent=order, meta={'csrf': False})
    partial_refund_args = {
        'order': order,
        'form': refund_form,
        'request_method': 'POST',
    }
    with patch('boxoffice.extapi.razorpay.refund_payment') as mock:
        mock.return_value = MockResponse(response_data={'id': buid()})
        with app.request_context(post_env):
            process_partial_refund_for_order(partial_refund_args)

    refund_transactions = order.transactions.filter_by(
        transaction_type=TransactionTypeEnum.REFUND
    ).all()
    assert isinstance(refund_transactions[0].refunded_at, datetime.datetime)
    assert refund_transactions[0].amount == decimal.Decimal(valid_refund_amount)
    assert refund_transactions[0].internal_note == formdata['internal_note']
    assert str(refund_transactions[0].note_to_user) == formdata['note_to_user']
    assert refund_transactions[0].refund_description == formdata['refund_description']

    invalid_refund_amount = 100000000
    formdata = {
        'amount': invalid_refund_amount,
    }
    refund_form = OrderRefundForm(data=formdata, parent=order, meta={'csrf': False})
    partial_refund_args = {
        'order': order,
        'form': refund_form,
        'request_method': 'POST',
    }
    with app.request_context(post_env):
        resp = process_partial_refund_for_order(partial_refund_args)

    assert resp.status_code == 403
    refund_transactions = order.transactions.filter_by(
        transaction_type=TransactionTypeEnum.REFUND
    ).all()
    assert refund_transactions[0].amount == decimal.Decimal(valid_refund_amount)

    resp = make_free_order(client)
    assert resp.status_code == 201
    resp_data = json.loads(resp.data)['result']
    order = Order.query.get(resp_data.get('order_id'))
    assert isinstance(order, Order)
    invalid_refund_amount = 100000000

    formdata = {
        'amount': invalid_refund_amount,
    }
    refund_form = OrderRefundForm(data=formdata, parent=order, meta={'csrf': False})
    partial_refund_args = {
        'order': order,
        'form': refund_form,
        'request_method': 'POST',
    }
    with app.request_context(post_env):
        refund_resp = process_partial_refund_for_order(partial_refund_args)

    assert refund_resp.status_code == 403
