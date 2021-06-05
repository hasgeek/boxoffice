from datetime import date
from types import SimpleNamespace

from sqlalchemy import event

from werkzeug.test import EnvironBuilder

from dateutil.relativedelta import relativedelta
import pytest

from boxoffice import app
from boxoffice.models import (
    DISCOUNT_TYPE,
    Category,
    DiscountCoupon,
    DiscountPolicy,
    Item,
    ItemCollection,
    Organization,
    Price,
    User,
    db,
)
from coaster.utils import utcnow


@pytest.fixture(scope='session')
def database(request):
    """Provide a database structure."""
    with app.app_context():
        db.create_all()

    @request.addfinalizer
    def drop_tables():
        with app.app_context():
            db.drop_all()

    return db


@pytest.fixture(scope='session')
def db_connection(database):
    """Return a database connection."""
    return database.engine.connect()


# This fixture borrowed from
# https://github.com/jeancochrane/pytest-flask-sqlalchemy/issues/46#issuecomment-829694672
@pytest.fixture(scope='function')
def db_session(database, db_connection):
    """Create a nested transaction for the test and roll it back after."""
    original_session = database.session
    transaction = db_connection.begin()
    database.session = database.create_scoped_session(
        options={'bind': db_connection, 'binds': {}}
    )
    database.session.begin_nested()

    # for handling tests that actually call `session.rollback()`
    # https://docs.sqlalchemy.org/en/13/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
    @event.listens_for(database.session, 'after_transaction_end')
    def restart_savepoint(session, transaction_in):
        if transaction_in.nested and not transaction_in._parent.nested:
            session.expire_all()
            session.begin_nested()

    yield database.session

    database.session.close()
    transaction.rollback()
    database.session = original_session


# Enable autouse to guard against tests that have implicit database access, or assume
# app context without a fixture
@pytest.fixture(autouse=True)
def client(request, db_session):
    """Provide a test client."""
    if 'noclient' in request.keywords:
        # To use this, annotate a test with:
        # @pytest.mark.noclient
        return None
    with app.app_context():  # Not required for test_client, but required for autouse
        with app.test_client() as test_client:
            yield test_client


@pytest.fixture
def post_env():
    builder = EnvironBuilder(method='POST')
    return builder.get_environ()


@pytest.fixture
def all_data(db_session):
    user = User(userid="U3_JesHfQ2OUmdihAXaAGQ", email="test@hasgeek.com")
    db_session.add(user)
    db_session.commit()

    one_month_from_now = date.today() + relativedelta(months=+1)

    rootconf = Organization(
        title='Rootconf',
        userid="U3_JesHfQ2OUmdihAXaAGQ",
        status=0,
        contact_email='test@gmail.com',
        details={
            'service_tax_no': 'xx',
            'address': '<h2 class="company-name">XYZ</h2> <p>Bangalore - 560034</p> <p>India</p>',
            'cin': '1234',
            'pan': 'abc',
            'website': 'https://www.test.com',
            'refund_policy': '<p>We offer full refund.</p>',
            'support_email': 'test@boxoffice.com',
            'ticket_faq': '<p>To cancel your ticket, please mail <a href="mailto:test@boxoffice.com">test@boxoffice.com</a> with your receipt number.</p>',
        },
    )
    db_session.add(rootconf)
    db_session.commit()

    rc2016 = ItemCollection(title='2016', organization=rootconf)
    db_session.add(rc2016)
    db_session.commit()

    category_conference = Category(title='Conference', item_collection=rc2016, seq=1)
    db_session.add(category_conference)
    category_workshop = Category(title='Workshop', item_collection=rc2016, seq=2)
    db_session.add(category_workshop)
    category_merch = Category(title='Merchandise', item_collection=rc2016, seq=3)
    db_session.add(category_merch)
    db_session.commit()

    with db_session.no_autoflush:
        conf_ticket = Item(
            title='Conference ticket',
            description='<p><i class="fa fa-calendar"></i>14 - 15 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>MLR Convention Center, JP Nagar</p><p>This ticket gets you access to rootconf conference on 14th and 15th April 2016.</p>',
            item_collection=rc2016,
            category=Category.query.filter_by(name='conference').first(),
            quantity_total=1000,
        )
        rc2016.items.append(conf_ticket)
        db_session.commit()

        expired_ticket = Item(
            title='Expired ticket',
            description='<p><i class="fa fa-calendar"></i>14 - 15 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>MLR Convention Center, JP Nagar</p><p>This ticket gets you access to rootconf conference on 14th and 15th April 2016.</p>',
            item_collection=rc2016,
            category=Category.query.filter_by(name='conference').first(),
            quantity_total=1000,
        )
        rc2016.items.append(expired_ticket)
        db_session.commit()

        price = Price(
            item=conf_ticket,
            title='Super Early Geek',
            start_at=utcnow(),
            end_at=one_month_from_now,
            amount=3500,
        )
        db_session.add(price)
        db_session.commit()

        single_day_conf_ticket = Item(
            title='Single Day',
            description='<p><i class="fa fa-calendar"></i>14 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>MLR Convention Center, JP Nagar</p><p>This ticket gets you access to rootconf conference on 14th April 2016.</p>',
            item_collection=rc2016,
            category=Category.query.filter_by(name='conference').first(),
            quantity_total=1000,
        )
        rc2016.items.append(single_day_conf_ticket)
        db_session.commit()

        single_day_price = Price(
            item=single_day_conf_ticket,
            title='Single Day',
            start_at=utcnow(),
            end_at=one_month_from_now,
            amount=2500,
        )
        db_session.add(single_day_price)
        db_session.commit()

        tshirt = Item(
            title='T-shirt',
            description='Rootconf',
            item_collection=rc2016,
            category=Category.query.filter_by(name='merchandise').first(),
            quantity_total=1000,
        )
        rc2016.items.append(tshirt)
        db_session.commit()

        tshirt_price = Price(
            item=tshirt,
            title='T-shirt',
            start_at=utcnow(),
            end_at=one_month_from_now,
            amount=500,
        )
        db_session.add(tshirt_price)
        db_session.commit()

        dns_workshop = Item(
            title='DNSSEC workshop',
            description='<p><i class="fa fa-calendar"></i>12 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>TERI, Domlur</p><p>This ticket gets you access to DNSSEC workshop 12th April 2016.</p>',
            item_collection=rc2016,
            category=Category.query.filter_by(name='workshop').first(),
            quantity_total=1000,
        )
        rc2016.items.append(dns_workshop)
        db_session.commit()

        dns_workshop_price = Price(
            item=dns_workshop,
            title='DNSSEC workshop early',
            start_at=utcnow(),
            end_at=one_month_from_now,
            amount=2500,
        )
        db_session.add(dns_workshop_price)
        db_session.commit()

        policy = DiscountPolicy(
            title='10% discount on rootconf',
            item_quantity_min=10,
            percentage=10,
            organization=rootconf,
        )
        policy.items.append(conf_ticket)
        db_session.add(policy)
        db_session.commit()

        tshirt_policy = DiscountPolicy(
            title='5% discount on 5 t-shirts',
            item_quantity_min=5,
            percentage=5,
            organization=rootconf,
        )
        tshirt_policy.items.append(tshirt)
        db_session.add(tshirt_policy)
        db_session.commit()

        discount_coupon1 = DiscountPolicy(
            title='15% discount for coupon code with STU',
            item_quantity_min=1,
            percentage=15,
            organization=rootconf,
            discount_type=DISCOUNT_TYPE.COUPON,
        )
        discount_coupon1.items.append(conf_ticket)
        db_session.add(discount_coupon1)
        db_session.commit()

        coupon1 = DiscountCoupon(code='coupon1', discount_policy=discount_coupon1)
        db_session.add(coupon1)
        db_session.commit()

        discount_coupon_expired_ticket = DiscountPolicy(
            title='15% discount for expired ticket',
            item_quantity_min=1,
            percentage=15,
            organization=rootconf,
            discount_type=DISCOUNT_TYPE.COUPON,
        )
        discount_coupon_expired_ticket.items.append(expired_ticket)
        db_session.add(discount_coupon_expired_ticket)
        db_session.commit()

        discount_coupon_expired_ticket_coupon = DiscountCoupon(
            code='couponex', discount_policy=discount_coupon_expired_ticket
        )
        db_session.add(discount_coupon_expired_ticket_coupon)
        db_session.commit()

        discount_coupon2 = DiscountPolicy(
            title='100% discount',
            item_quantity_min=1,
            percentage=100,
            organization=rootconf,
            discount_type=DISCOUNT_TYPE.COUPON,
        )
        discount_coupon2.items.append(conf_ticket)
        db_session.add(discount_coupon1)
        db_session.commit()

        coupon2 = DiscountCoupon(code='coupon2', discount_policy=discount_coupon2)
        db_session.add(coupon2)
        db_session.commit()

        coupon3 = DiscountCoupon(code='coupon3', discount_policy=discount_coupon2)
        db_session.add(coupon3)
        db_session.commit()

        forever_early_geek = DiscountPolicy(
            title='Forever Early Geek',
            item_quantity_min=1,
            is_price_based=True,
            discount_type=DISCOUNT_TYPE.COUPON,
            organization=rootconf,
        )
        forever_early_geek.items.append(conf_ticket)
        db_session.add(forever_early_geek)
        db_session.commit()

        forever_coupon = DiscountCoupon(
            code='forever', discount_policy=forever_early_geek
        )
        db_session.add(forever_coupon)
        db_session.commit()

        noprice_discount = DiscountPolicy(
            title='noprice',
            item_quantity_min=1,
            is_price_based=True,
            discount_type=DISCOUNT_TYPE.COUPON,
            organization=rootconf,
        )
        noprice_discount.items.append(conf_ticket)
        db_session.add(noprice_discount)
        db_session.commit()

        noprice_coupon = DiscountCoupon(
            code='noprice', discount_policy=noprice_discount
        )
        db_session.add(noprice_coupon)
        db_session.commit()

        forever_unlimited_coupon = DiscountCoupon(
            code='unlimited', discount_policy=forever_early_geek, usage_limit=500
        )
        db_session.add(forever_unlimited_coupon)
        db_session.commit()

        discount_price = Price(
            item=conf_ticket,
            discount_policy=forever_early_geek,
            title='Forever Early Geek',
            start_at=utcnow(),
            end_at=one_month_from_now,
            amount=3400,
        )
        db_session.add(discount_price)
        db_session.commit()

        unlimited_geek = DiscountPolicy(
            title='Unlimited Geek',
            item_quantity_min=1,
            discount_type=DISCOUNT_TYPE.COUPON,
            percentage=10,
            organization=rootconf,
        )
        unlimited_geek.items.append(conf_ticket)
        db_session.add(unlimited_geek)
        db_session.commit()

        unlimited_coupon = DiscountCoupon(
            code='unlimited', discount_policy=unlimited_geek, usage_limit=500
        )
        db_session.add(unlimited_coupon)
        db_session.commit()

        zero_discount = DiscountPolicy(
            title='Zero Discount',
            item_quantity_min=1,
            is_price_based=True,
            discount_type=DISCOUNT_TYPE.COUPON,
            organization=rootconf,
        )
        zero_discount.items.append(conf_ticket)
        db_session.add(zero_discount)
        db_session.commit()

        zero_coupon = DiscountCoupon(code='zerodi', discount_policy=zero_discount)
        db_session.add(zero_coupon)
        db_session.commit()

        zero_discount_price = Price(
            item=conf_ticket,
            discount_policy=zero_discount,
            title='Zero Discount',
            start_at=utcnow(),
            end_at=one_month_from_now,
            amount=3600,
        )
        db_session.add(zero_discount_price)
        db_session.commit()

        bulk = DiscountPolicy.make_bulk(
            'signed',
            organization=rootconf,
            title='Signed',
            percentage=10,
            bulk_coupon_usage_limit=2,
        )
        bulk.items.append(conf_ticket)
        db_session.add(bulk)
        db_session.commit()

    return SimpleNamespace(**locals())
