# pylint: disable=redefined-outer-name
from datetime import date
from types import SimpleNamespace

from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import close_all_sessions
from werkzeug.test import EnvironBuilder
import pytest
import sqlalchemy as sa

from coaster.utils import utcnow

from boxoffice import app
from boxoffice.models import (
    Category,
    DiscountCoupon,
    DiscountPolicy,
    DiscountTypeEnum,
    Item,
    ItemCollection,
    Organization,
    Price,
    User,
    db,
)


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
    with app.app_context():
        yield database.engine.connect()


class RemoveIsRollback:
    """Change session.remove() to session.rollback()."""

    def __init__(self, session, rollback_provider):
        self.session = session
        self.original_remove = session.remove
        self.rollback_provider = rollback_provider

    def __enter__(self):
        """Replace ``session.remove`` during the `with` context."""

    def __exit__(self, exc_type, exc_value, traceback):
        """Restore ``session.remove`` after the `with` context."""
        self.session.remove = self.original_remove


@pytest.fixture()
def db_session(database, db_connection):
    """Empty the database after each use of the fixture."""
    with RemoveIsRollback(database.session, lambda: database.session.rollback):
        yield database.session
    close_all_sessions()

    # Iterate through all database engines and empty their tables
    with app.app_context():
        for bind in [None] + list(app.config.get('SQLALCHEMY_BINDS') or ()):
            engine = database.engines[bind]
            with engine.begin() as connection:
                connection.execute(
                    sa.text(
                        '''
    DO $$
    DECLARE tablenames text;
    BEGIN
        tablenames := string_agg(
            quote_ident(schemaname) || '.' || quote_ident(tablename), ', ')
            FROM pg_tables WHERE schemaname = 'public';
        EXECUTE 'TRUNCATE TABLE ' || tablenames || ' RESTART IDENTITY';
    END; $$'''
                    )
                )


# Enable autouse to guard against tests that have implicit database access, or assume
# app context without a fixture
@pytest.fixture(autouse=True)
def client(request):
    """Provide a test client."""
    if 'noclient' in request.keywords:
        # To use this, annotate a test with:
        # @pytest.mark.noclient
        yield None
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture()
def post_env():
    builder = EnvironBuilder(method='POST')
    return builder.get_environ()


@pytest.fixture()
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
            'address': '<h2 class="company-name">XYZ</h2> <p>Bangalore - 560034</p>'
            ' <p>India</p>',
            'cin': '1234',
            'pan': 'abc',
            'website': 'https://www.test.com',
            'refund_policy': '<p>We offer full refund.</p>',
            'support_email': 'test@boxoffice.com',
            'ticket_faq': '<p>To cancel your ticket, please mail <a '
            'href="mailto:test@boxoffice.com">test@boxoffice.com</a> with your receipt'
            ' number.</p>',
        },
    )
    db_session.add(rootconf)
    db_session.commit()

    rc2016 = ItemCollection(title='2016', organization=rootconf)
    db_session.add(rc2016)
    db_session.commit()

    category_conference = Category(title='Conference', menu=rc2016, seq=1)
    db_session.add(category_conference)
    category_workshop = Category(title='Workshop', menu=rc2016, seq=2)
    db_session.add(category_workshop)
    category_merch = Category(title='Merchandise', menu=rc2016, seq=3)
    db_session.add(category_merch)
    db_session.commit()

    with db_session.no_autoflush:
        conf_ticket = Item(
            title='Conference ticket',
            description='<p><i class="fa fa-calendar"></i>14 - 15 April 2016'
            '</p><p><i class="fa fa-map-marker ticket-venue"></i>MLR Convention Center,'
            ' JP Nagar</p><p>This ticket gets you access to rootconf conference on 14th'
            ' and 15th April 2016.</p>',
            menu=rc2016,
            category=Category.query.filter_by(name='conference').one(),
            quantity_total=1000,
        )
        rc2016.tickets.append(conf_ticket)
        db_session.commit()

        expired_ticket = Item(
            title='Expired ticket',
            description='<p><i class="fa fa-calendar"></i>14 - 15 April 2016'
            '</p><p><i class="fa fa-map-marker ticket-venue"></i>MLR Convention Center,'
            ' JP Nagar</p><p>This ticket gets you access to rootconf conference on 14th'
            ' and 15th April 2016.</p>',
            menu=rc2016,
            category=Category.query.filter_by(name='conference').one(),
            quantity_total=1000,
        )
        rc2016.tickets.append(expired_ticket)
        db_session.commit()

        price = Price(
            ticket=conf_ticket,
            title='Super Early Geek',
            start_at=utcnow(),
            end_at=one_month_from_now,
            amount=3500,
        )
        db_session.add(price)
        db_session.commit()

        single_day_conf_ticket = Item(
            title='Single Day',
            description='<p><i class="fa fa-calendar"></i>14 April 2016'
            '</p><p><i class="fa fa-map-marker ticket-venue"></i>MLR Convention Center,'
            ' JP Nagar</p><p>This ticket gets you access to rootconf conference on 14th'
            ' April 2016.</p>',
            menu=rc2016,
            category=Category.query.filter_by(name='conference').one(),
            quantity_total=1000,
        )
        rc2016.tickets.append(single_day_conf_ticket)
        db_session.commit()

        single_day_price = Price(
            ticket=single_day_conf_ticket,
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
            menu=rc2016,
            category=Category.query.filter_by(name='merchandise').one(),
            quantity_total=1000,
        )
        rc2016.tickets.append(tshirt)
        db_session.commit()

        tshirt_price = Price(
            ticket=tshirt,
            title='T-shirt',
            start_at=utcnow(),
            end_at=one_month_from_now,
            amount=500,
        )
        db_session.add(tshirt_price)
        db_session.commit()

        dns_workshop = Item(
            title='DNSSEC workshop',
            description='<p><i class="fa fa-calendar"></i>12 April 2016'
            '</p><p><i class="fa fa-map-marker ticket-venue"></i>TERI, Domlur</p>'
            '<p>This ticket gets you access to DNSSEC workshop 12th April 2016.</p>',
            menu=rc2016,
            category=Category.query.filter_by(name='workshop').one(),
            quantity_total=1000,
        )
        rc2016.tickets.append(dns_workshop)
        db_session.commit()

        dns_workshop_price = Price(
            ticket=dns_workshop,
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
        policy.tickets.append(conf_ticket)
        db_session.add(policy)
        db_session.commit()

        tshirt_policy = DiscountPolicy(
            title='5% discount on 5 t-shirts',
            item_quantity_min=5,
            percentage=5,
            organization=rootconf,
        )
        tshirt_policy.tickets.append(tshirt)
        db_session.add(tshirt_policy)
        db_session.commit()

        discount_coupon1 = DiscountPolicy(
            title='15% discount for coupon code with STU',
            item_quantity_min=1,
            percentage=15,
            organization=rootconf,
            discount_type=DiscountTypeEnum.COUPON,
        )
        discount_coupon1.tickets.append(conf_ticket)
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
            discount_type=DiscountTypeEnum.COUPON,
        )
        discount_coupon_expired_ticket.tickets.append(expired_ticket)
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
            discount_type=DiscountTypeEnum.COUPON,
        )
        discount_coupon2.tickets.append(conf_ticket)
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
            discount_type=DiscountTypeEnum.COUPON,
            organization=rootconf,
        )
        forever_early_geek.tickets.append(conf_ticket)
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
            discount_type=DiscountTypeEnum.COUPON,
            organization=rootconf,
        )
        noprice_discount.tickets.append(conf_ticket)
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
            ticket=conf_ticket,
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
            discount_type=DiscountTypeEnum.COUPON,
            percentage=10,
            organization=rootconf,
        )
        unlimited_geek.tickets.append(conf_ticket)
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
            discount_type=DiscountTypeEnum.COUPON,
            organization=rootconf,
        )
        zero_discount.tickets.append(conf_ticket)
        db_session.add(zero_discount)
        db_session.commit()

        zero_coupon = DiscountCoupon(code='zerodi', discount_policy=zero_discount)
        db_session.add(zero_coupon)
        db_session.commit()

        zero_discount_price = Price(
            ticket=conf_ticket,
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
        bulk.tickets.append(conf_ticket)
        db_session.add(bulk)
        db_session.commit()

    return SimpleNamespace(**locals())
