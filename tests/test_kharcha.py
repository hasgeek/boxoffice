import decimal
import json
from typing import cast

import pytest
from flask import url_for

from coaster.utils import make_name

from boxoffice import app
from boxoffice.models import DiscountCoupon, DiscountPolicy, Ticket


@pytest.mark.usefixtures('all_data')
def test_undiscounted_kharcha(client) -> None:
    first_item = Ticket.query.filter_by(name='conference-ticket').one()
    undiscounted_quantity = 2
    kharcha_req = {
        'line_items': [
            {'ticket_id': str(first_item.id), 'quantity': undiscounted_quantity}
        ]
    }
    resp = client.post(
        url_for('kharcha'),
        data=json.dumps(kharcha_req),
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )

    assert resp.status_code == 200
    resp_json = json.loads(resp.get_data())
    # Test that the price is correct
    current_price = first_item.current_price()
    assert current_price is not None
    assert (
        resp_json.get('line_items')[str(first_item.id)].get('final_amount')
        == undiscounted_quantity * current_price.amount
    )

    policy_ids = resp_json.get('line_items')[str(first_item.id)].get(
        'discount_policy_ids'
    )
    assert policy_ids == []
    current_price = first_item.current_price()
    assert current_price is not None
    assert (
        resp_json.get('line_items')[str(first_item.id)].get('final_amount')
        == undiscounted_quantity * current_price.amount
    )


@pytest.mark.usefixtures('all_data')
def test_expired_ticket_kharcha(client) -> None:
    expired_ticket = Ticket.query.filter_by(name='expired-ticket').one()
    quantity = 2
    kharcha_req = {
        'line_items': [{'ticket_id': str(expired_ticket.id), 'quantity': quantity}]
    }
    resp = client.post(
        url_for('kharcha'),
        data=json.dumps(kharcha_req),
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )

    assert resp.status_code == 200
    resp_json = json.loads(resp.get_data())
    # Test that the price is None

    assert (
        resp_json.get('line_items')[str(expired_ticket.id)].get('base_amount') is None
    )


@pytest.mark.usefixtures('all_data')
def test_expired_discounted_item_kharcha(client) -> None:
    expired_ticket = Ticket.query.filter_by(name='expired-ticket').one()
    quantity = 2
    coupon = DiscountCoupon.query.filter_by(code='couponex').one()
    kharcha_req = {
        'line_items': [{'ticket_id': str(expired_ticket.id), 'quantity': quantity}],
        'discount_coupons': [coupon.code],
    }
    resp = client.post(
        url_for('kharcha'),
        data=json.dumps(kharcha_req),
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )

    assert resp.status_code == 200
    resp_json = json.loads(resp.get_data())
    # Test that the price is None
    assert (
        resp_json.get('line_items')[str(expired_ticket.id)].get('base_amount') is None
    )


@pytest.mark.usefixtures('all_data')
def test_discounted_bulk_kharcha(client) -> None:
    first_item = Ticket.query.filter_by(name='conference-ticket').one()
    discounted_quantity = 10
    kharcha_req = {
        'line_items': [
            {'ticket_id': str(first_item.id), 'quantity': discounted_quantity}
        ]
    }
    resp = client.post(
        url_for('kharcha'),
        data=json.dumps(kharcha_req),
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )
    assert resp.status_code == 200
    resp_json = json.loads(resp.get_data())

    current_price = first_item.current_price()
    assert current_price is not None
    base_amount = discounted_quantity * current_price.amount
    discount_policy = first_item.discount_policies.first()
    assert discount_policy is not None
    assert discount_policy.percentage is not None
    discounted_amount = (discount_policy.percentage * base_amount) / decimal.Decimal(
        100
    )
    assert (
        resp_json.get('line_items')[str(first_item.id)].get('final_amount')
        == base_amount - discounted_amount
    )

    expected_discount_policy_ids = [
        str(DiscountPolicy.query.filter_by(title='10% discount on rootconf').one().id)
    ]
    policy_ids = [
        str(policy)
        for policy in resp_json.get('line_items')[str(first_item.id)].get(
            'discount_policy_ids'
        )
    ]

    # Test that all the discount policies are returned
    for expected_policy_id in expected_discount_policy_ids:
        assert expected_policy_id in policy_ids


@pytest.mark.usefixtures('all_data')
def test_discounted_coupon_kharcha(client) -> None:
    first_item = Ticket.query.filter_by(name='conference-ticket').one()
    coupon: DiscountCoupon = DiscountCoupon.query.filter_by(code='coupon1').one()
    discounted_quantity = 1
    kharcha_req = {
        'line_items': [
            {'ticket_id': str(first_item.id), 'quantity': discounted_quantity}
        ],
        'discount_coupons': [coupon.code],
    }
    resp = client.post(
        url_for('kharcha'),
        data=json.dumps(kharcha_req),
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )
    assert resp.status_code == 200
    resp_json = json.loads(resp.get_data())

    current_price = first_item.current_price()
    assert current_price is not None
    base_amount = discounted_quantity * current_price.amount
    discount_policy = coupon.discount_policy
    assert discount_policy is not None
    assert discount_policy.percentage is not None
    discounted_amount = (discount_policy.percentage * base_amount) / decimal.Decimal(
        100
    )
    assert (
        resp_json.get('line_items')[str(first_item.id)].get('final_amount')
        == base_amount - discounted_amount
    )

    expected_discount_policy_ids = [str(coupon.discount_policy_id)]
    policy_ids = [
        str(policy)
        for policy in resp_json.get('line_items')[str(first_item.id)].get(
            'discount_policy_ids'
        )
    ]

    # Test that all the discount policies are returned
    for expected_policy_id in expected_discount_policy_ids:
        assert expected_policy_id in policy_ids


@pytest.mark.usefixtures('all_data')
def test_signed_discounted_coupon_kharcha(client) -> None:
    first_item = Ticket.query.filter_by(name='conference-ticket').one()
    signed_policy = DiscountPolicy.query.filter_by(name='signed').one()
    code = signed_policy.gen_signed_code()
    discounted_quantity = 2
    kharcha_req = {
        'line_items': [
            {'ticket_id': str(first_item.id), 'quantity': discounted_quantity}
        ],
        'discount_coupons': [code],
    }
    resp = client.post(
        url_for('kharcha'),
        data=json.dumps(kharcha_req),
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )
    assert resp.status_code == 200
    resp_json = json.loads(resp.get_data())

    current_price = first_item.current_price()
    assert current_price is not None
    base_amount = discounted_quantity * current_price.amount
    assert signed_policy.percentage is not None
    discounted_amount = (signed_policy.percentage * base_amount) / decimal.Decimal(100)
    assert (
        resp_json.get('line_items')[str(first_item.id)].get('final_amount')
        == base_amount - discounted_amount
    )

    expected_discount_policy_ids = [str(signed_policy.id)]
    policy_ids = [
        str(policy)
        for policy in resp_json.get('line_items')[str(first_item.id)].get(
            'discount_policy_ids'
        )
    ]

    # Test that all the discount policies are returned
    for expected_policy_id in expected_discount_policy_ids:
        assert expected_policy_id in policy_ids


@pytest.mark.usefixtures('all_data')
def test_unlimited_coupon_kharcha(client) -> None:
    first_item = Ticket.query.filter_by(name='conference-ticket').one()
    coupon_code = 'unlimited'
    discounted_quantity = 5
    kharcha_req = {
        'line_items': [
            {'ticket_id': str(first_item.id), 'quantity': discounted_quantity}
        ],
        'discount_coupons': [coupon_code],
    }

    resp = client.post(
        url_for('kharcha'),
        data=json.dumps(kharcha_req),
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )
    resp_json = json.loads(resp.get_data())
    assert resp.status_code == 200

    current_price = first_item.current_price()
    assert current_price is not None
    base_amount = discounted_quantity * current_price.amount
    discount_policy = DiscountPolicy.query.filter_by(
        name=make_name('Unlimited Geek')
    ).one()
    discounted_amount = discounted_quantity * (
        (cast(int, discount_policy.percentage) / decimal.Decimal(100))
        * current_price.amount
    )
    assert (
        resp_json.get('line_items')[str(first_item.id)].get('final_amount')
        == base_amount - discounted_amount
    )

    policy_ids = [
        str(policy)
        for policy in resp_json.get('line_items')[str(first_item.id)].get(
            'discount_policy_ids'
        )
    ]
    expected_discount_policy_ids = [discount_policy.id]
    # Test that all the discount policies are returned
    for expected_policy_id in expected_discount_policy_ids:
        assert str(expected_policy_id) in policy_ids


@pytest.mark.usefixtures('all_data')
def test_coupon_limit(client) -> None:
    first_item = Ticket.query.filter_by(name='conference-ticket').one()
    coupon = DiscountCoupon.query.filter_by(code='coupon1').one()
    discounted_quantity = 2
    kharcha_req = {
        'line_items': [
            {'ticket_id': str(first_item.id), 'quantity': discounted_quantity}
        ],
        'discount_coupons': [coupon.code],
    }
    resp = client.post(
        url_for('kharcha'),
        data=json.dumps(kharcha_req),
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )
    assert resp.status_code == 200
    resp_json = json.loads(resp.get_data())

    current_price = first_item.current_price()
    assert current_price is not None
    base_amount = discounted_quantity * current_price.amount
    assert coupon.discount_policy.percentage is not None
    discounted_amount = (
        coupon.discount_policy.percentage * current_price.amount
    ) / decimal.Decimal(100)
    assert (
        resp_json.get('line_items')[str(first_item.id)].get('final_amount')
        == base_amount - discounted_amount
    )

    expected_discount_policy_ids = [str(coupon.discount_policy_id)]
    policy_ids = [
        str(policy)
        for policy in resp_json.get('line_items')[str(first_item.id)].get(
            'discount_policy_ids'
        )
    ]

    # Test that all the discount policies are returned
    for expected_policy_id in expected_discount_policy_ids:
        assert expected_policy_id in policy_ids


@pytest.mark.usefixtures('all_data')
def test_discounted_price_kharcha(client) -> None:
    first_item = Ticket.query.filter_by(name='conference-ticket').one()
    coupon = DiscountCoupon.query.filter_by(code='forever').one()
    discounted_quantity = 1
    kharcha_req = {
        'line_items': [
            {'ticket_id': str(first_item.id), 'quantity': discounted_quantity}
        ],
        'discount_coupons': [coupon.code],
    }
    resp = client.post(
        url_for('kharcha'),
        data=json.dumps(kharcha_req),
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )
    assert resp.status_code == 200
    resp_json = json.loads(resp.get_data())

    discounted_price = next(
        price for price in first_item.prices if price.name == 'forever-early-geek'
    )
    assert resp_json.get('line_items')[str(first_item.id)].get('final_amount') == int(
        discounted_price.amount
    )
    expected_discount_policy_ids = [str(coupon.discount_policy_id)]
    policy_ids = [
        str(policy)
        for policy in resp_json.get('line_items')[str(first_item.id)].get(
            'discount_policy_ids'
        )
    ]

    # Test that all the discount policies are returned
    for expected_policy_id in expected_discount_policy_ids:
        assert expected_policy_id in policy_ids


@pytest.mark.usefixtures('all_data')
def test_discount_policy_without_price_kharcha(client) -> None:
    first_item = Ticket.query.filter_by(name='conference-ticket').one()
    coupon = DiscountCoupon.query.filter_by(code='noprice').one()
    discounted_quantity = 1
    kharcha_req = {
        'line_items': [
            {'ticket_id': str(first_item.id), 'quantity': discounted_quantity}
        ],
        'discount_coupons': [coupon.code],
    }
    # print first_item.discount_policies.all()
    resp = client.post(
        url_for('kharcha'),
        data=json.dumps(kharcha_req),
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )
    # print resp.status_code
    assert resp.status_code == 200
    resp_json = json.loads(resp.get_data())

    assert resp_json.get('line_items')[str(first_item.id)].get(
        'discounted_amount'
    ) == decimal.Decimal(0)


@pytest.mark.usefixtures('all_data')
def test_zero_discounted_price_kharcha(client) -> None:
    first_item = Ticket.query.filter_by(name='conference-ticket').one()
    coupon = DiscountCoupon.query.filter_by(code='zerodi').one()
    discounted_quantity = 1
    kharcha_req = {
        'line_items': [
            {'ticket_id': str(first_item.id), 'quantity': discounted_quantity}
        ],
        'discount_coupons': [coupon.code],
    }
    resp = client.post(
        url_for('kharcha'),
        data=json.dumps(kharcha_req),
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )
    assert resp.status_code == 200
    resp_json = json.loads(resp.get_data())
    discounted_price = next(
        price for price in first_item.prices if price.name == 'zero-discount'
    )
    assert resp_json.get('line_items')[str(first_item.id)].get('final_amount') != int(
        discounted_price.amount
    )
    expected_discount_policy_ids = [str(coupon.discount_policy_id)]
    policy_ids = [
        str(policy)
        for policy in resp_json.get('line_items')[str(first_item.id)].get(
            'discount_policy_ids'
        )
    ]

    # Test that all the discount policies are returned
    for expected_policy_id in expected_discount_policy_ids:
        assert expected_policy_id not in policy_ids


@pytest.mark.usefixtures('all_data')
def test_discounted_complex_kharcha(client) -> None:
    first_item = Ticket.query.filter_by(name='conference-ticket').one()
    discounted_quantity = 9
    coupon2 = DiscountCoupon.query.filter_by(code='coupon2').one()
    coupon3 = DiscountCoupon.query.filter_by(code='coupon3').one()
    kharcha_req = {
        'line_items': [
            {'ticket_id': str(first_item.id), 'quantity': discounted_quantity}
        ],
        'discount_coupons': [coupon2.code, coupon3.code],
    }

    resp = client.post(
        url_for('kharcha'),
        data=json.dumps(kharcha_req),
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )

    assert resp.status_code == 200
    resp_json = json.loads(resp.get_data())

    current_price = first_item.current_price()
    assert current_price is not None
    base_amount = discounted_quantity * current_price.amount
    discounted_amount = 2 * current_price.amount
    assert (
        resp_json.get('line_items')[str(first_item.id)].get('final_amount')
        == base_amount - discounted_amount
    )

    expected_discount_policy_ids = [
        str(coupon2.discount_policy_id),
        str(coupon3.discount_policy_id),
    ]
    policy_ids = [
        str(policy)
        for policy in resp_json.get('line_items')[str(first_item.id)].get(
            'discount_policy_ids'
        )
    ]
    # Test that all the discount policies are returned
    for expected_policy_id in expected_discount_policy_ids:
        assert expected_policy_id in policy_ids
