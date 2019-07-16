# -*- coding: utf-8 -*-

import pytest
from boxoffice import app
from boxoffice.models import (
    Category,
    DiscountCoupon,
    DiscountPolicy,
    Item,
    ItemCollection,
    Organization,
    db,
)


@pytest.fixture(scope='session')
def test_client():
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = app.test_client()

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    # anything after yield is teardown code
    ctx.pop()


@pytest.fixture(scope='session')
def test_db(test_client):
    # Create the database and the database table
    db.create_all()

    yield db  # this is where the testing happens!

    # anything after yield is teardown code
    db.session.rollback()
    db.session.remove()
    db.drop_all()


@pytest.fixture(scope='session')
def new_org(test_db):
    org = Organization(
        name=u"test-org",
        title=u"Test Org",
        userid=u"testorguserid",
        contact_email=u"testemail@hasgeek.com",
    )
    test_db.session.add(org)
    test_db.session.commit()
    return org


@pytest.fixture(scope='session')
def new_item_collection(test_db, new_org):
    ic = ItemCollection(
        name=u"test-item-collection",
        title=u"Test Item Collection",
        description=u"Test Description",
        organization=new_org
    )
    test_db.session.add(ic)
    test_db.session.commit()
    return ic


@pytest.fixture(scope='session')
def new_category(test_db, new_item_collection):
    category = Category(
        name=u"test-category",
        title=u"Test Category",
        item_collection=new_item_collection,
        seq=0
    )
    test_db.session.add(category)
    test_db.session.commit()
    return category


@pytest.fixture(scope='session')
def new_item(test_db, new_item_collection, new_category):
    item = Item(
        name=u"test-item",
        title=u"Test Item",
        description=u"Test Description",
        seq=0,
        item_collection=new_item_collection,
        category=new_category,
    )
    test_db.session.add(item)
    test_db.session.commit()
    return item


@pytest.fixture(scope='session')
def new_item_another(test_db, new_item_collection, new_category):
    item = Item(
        name=u"test-item-another",
        title=u"Test Item Another",
        description=u"Test Description",
        seq=0,
        item_collection=new_item_collection,
        category=new_category,
    )
    test_db.session.add(item)
    test_db.session.commit()
    return item


@pytest.fixture(scope='session')
def new_discount_policy(test_db, new_org, new_item, new_item_another):
    dp = DiscountPolicy(
        name=u"test-discount-policy",
        title=u"Test Discount Policy",
        organization=new_org
    )
    test_db.session.add(dp)
    new_item.discount_policies.append(dp)
    new_item_another.discount_policies.append(dp)
    test_db.session.commit()
    return dp


@pytest.fixture(scope='session')
def new_discount_policy_another(test_db, new_org, new_item_another):
    dp = DiscountPolicy(
        name=u"test-discount-policy-another",
        title=u"Test Discount Policy Another",
        organization=new_org
    )
    test_db.session.add(dp)
    new_item_another.discount_policies.append(dp)
    test_db.session.commit()
    return dp


@pytest.fixture(scope='session')
def new_discount_coupon(test_db, new_discount_policy):
    dc = DiscountCoupon(code=u"TESTCODE", discount_policy=new_discount_policy)
    test_db.session.add(dc)
    test_db.session.commit()
    return dc

