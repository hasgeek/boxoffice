import json

import pytest

from boxoffice import app
from boxoffice.models import ItemCollection

expected_keys = ['categories', 'currency', 'html', 'refund_policy']
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


@pytest.fixture
def resp(client, all_data):
    ic = ItemCollection.query.first()
    return client.get(
        f'/ic/{ic.id}',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )


def test_status(resp):
    assert resp.status_code == 200


def test_root_keys(resp):
    data = json.loads(resp.data)
    assert sorted(data.keys()) == sorted(expected_keys)


def test_category_keys(resp):
    data = json.loads(resp.data)
    assert sorted([cat['name'] for cat in data['categories']]) == sorted(
        expected_categories_names
    )

    for category in data['categories']:
        expected_items = expected_data[category['name']]
        assert sorted([c['name'] for c in category['items']]) == sorted(
            expected_items.keys()
        )

        for item in category['items']:
            expected_item_data = expected_items[item['name']]
            assert item['title'] == expected_item_data['title']
            assert item['price'] == expected_item_data['price']
            assert item['description'] == expected_item_data['description']
            assert item['quantity_total'] == expected_item_data['quantity_total']
