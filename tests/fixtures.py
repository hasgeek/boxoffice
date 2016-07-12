#!/usr/bin/env python

from boxoffice.models import *
from datetime import date
from dateutil.relativedelta import relativedelta


def init_data():
    db.drop_all()
    db.create_all()

    user = User(userid="U3_JesHfQ2OUmdihAXaAGQ", email="test@hasgeek.com")
    db.session.add(user)
    db.session.commit()

    one_month_from_now = date.today() + relativedelta(months=+1)

    rootconf = Organization(title='Rootconf', userid="U3_JesHfQ2OUmdihAXaAGQ",
        status=0, contact_email=u'test@gmail.com',
        details={'service_tax_no': 'xx', 'address': u'<h2 class="company-name">XYZ</h2> <p>Bangalore - 560034</p> <p>India</p>', 'cin': u'1234', 'pan': u'abc', 'website': u'https://www.test.com'})
    db.session.add(rootconf)
    db.session.commit()

    rc2016 = ItemCollection(title='2016', organization=rootconf)
    db.session.add(rc2016)
    db.session.commit()

    category_conference = Category(title='Conference', item_collection=rc2016, seq=1)
    db.session.add(category_conference)
    category_workshop = Category(title='Workshop', item_collection=rc2016, seq=2)
    db.session.add(category_workshop)
    category_merch = Category(title='Merchandise', item_collection=rc2016, seq=3)
    db.session.add(category_merch)
    db.session.commit()

    # import IPython; IPython.embed()
    with db.session.no_autoflush:
        conf_ticket = Item(title='Conference ticket', description='<p><i class="fa fa-calendar"></i>14 - 15 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>MLR Convention Center, JP Nagar</p><p>This ticket gets you access to rootconf conference on 14th and 15th April 2016.</p>', item_collection=rc2016, category=Category.query.filter_by(name='conference').first(), quantity_total=1000)
        rc2016.items.append(conf_ticket)
        db.session.commit()

        price = Price(item=conf_ticket, title='Super Early Geek', start_at=date.today(), end_at=one_month_from_now, amount=3500)
        db.session.add(price)
        db.session.commit()

        single_day_conf_ticket = Item(title='Single Day', description='<p><i class="fa fa-calendar"></i>14 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>MLR Convention Center, JP Nagar</p><p>This ticket gets you access to rootconf conference on 14th April 2016.</p>', item_collection=rc2016, category=Category.query.filter_by(name='conference').first(), quantity_total=1000)
        rc2016.items.append(single_day_conf_ticket)
        db.session.commit()

        single_day_price = Price(item=single_day_conf_ticket, title='Single Day', start_at=date.today(), end_at=one_month_from_now, amount=2500)
        db.session.add(single_day_price)
        db.session.commit()

        tshirt = Item(title='T-shirt', description='Rootconf', item_collection=rc2016, category=Category.query.filter_by(name='merchandise').first(), quantity_total=1000)
        rc2016.items.append(tshirt)
        db.session.commit()

        tshirt_price = Price(item=tshirt, title='T-shirt', start_at=date.today(), end_at=one_month_from_now, amount=500)
        db.session.add(tshirt_price)
        db.session.commit()

        dns_workshop = Item(title='DNSSEC workshop', description='<p><i class="fa fa-calendar"></i>12 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>TERI, Domlur</p><p>This ticket gets you access to DNSSEC workshop 12th April 2016.</p>', item_collection=rc2016, category=Category.query.filter_by(name='workshop').first(), quantity_total=1000)
        rc2016.items.append(dns_workshop)
        db.session.commit()

        dns_workshop_price = Price(item=dns_workshop, title='DNSSEC workshop early', start_at=date.today(), end_at=one_month_from_now, amount=2500)
        db.session.add(dns_workshop_price)
        db.session.commit()

        policy = DiscountPolicy(title='10% discount on rootconf', item_quantity_min=10, percentage=10, organization=rootconf)
        policy.items.append(conf_ticket)
        db.session.add(policy)
        db.session.commit()

        tshirt_policy = DiscountPolicy(title='5% discount on 5 t-shirts', item_quantity_min=5, percentage=5, organization=rootconf)
        tshirt_policy.items.append(tshirt)
        db.session.add(tshirt_policy)
        db.session.commit()

        discount_coupon1 = DiscountPolicy(title='15% discount for coupon code with STU', item_quantity_min=1, percentage=15, organization=rootconf, discount_type=DISCOUNT_TYPE.COUPON)
        discount_coupon1.items.append(conf_ticket)
        db.session.add(discount_coupon1)
        db.session.commit()

        coupon1 = DiscountCoupon(code='coupon1', discount_policy=discount_coupon1)
        db.session.add(coupon1)
        db.session.commit()

        discount_coupon2 = DiscountPolicy(title='100% discount', item_quantity_min=1, percentage=100, organization=rootconf, discount_type=DISCOUNT_TYPE.COUPON)
        discount_coupon2.items.append(conf_ticket)
        db.session.add(discount_coupon1)
        db.session.commit()

        coupon2 = DiscountCoupon(code='coupon2', discount_policy=discount_coupon2)
        db.session.add(coupon2)
        db.session.commit()

        coupon3 = DiscountCoupon(code='coupon3', discount_policy=discount_coupon2)
        db.session.add(coupon3)
        db.session.commit()

        forever_early_geek = DiscountPolicy(title='Forever Early Geek',
            item_quantity_min=1,
            is_price_based=True,
            discount_type=DISCOUNT_TYPE.COUPON,
            organization=rootconf)
        forever_early_geek.items.append(conf_ticket)
        db.session.add(forever_early_geek)
        db.session.commit()

        forever_coupon = DiscountCoupon(code='forever', discount_policy=forever_early_geek)
        db.session.add(forever_coupon)
        db.session.commit()

        forever_unlimited_coupon = DiscountCoupon(code='unlimited', discount_policy=forever_early_geek,
            usage_limit=500)
        db.session.add(forever_unlimited_coupon)
        db.session.commit()

        discount_price = Price(item=conf_ticket,
            discount_policy=forever_early_geek, title='Forever Early Geek',
            start_at=date.today(), end_at=one_month_from_now, amount=3400)
        db.session.add(discount_price)
        db.session.commit()

        zero_discount = DiscountPolicy(title='Zero Discount',
            item_quantity_min=1,
            is_price_based=True,
            discount_type=DISCOUNT_TYPE.COUPON,
            organization=rootconf)
        zero_discount.items.append(conf_ticket)
        db.session.add(zero_discount)
        db.session.commit()

        zero_coupon = DiscountCoupon(code='zerodi', discount_policy=zero_discount)
        db.session.add(zero_coupon)
        db.session.commit()

        zero_discount_price = Price(item=conf_ticket,
            discount_policy=zero_discount, title='Zero Discount',
            start_at=date.today(), end_at=one_month_from_now, amount=3600)
        db.session.add(zero_discount_price)
        db.session.commit()
