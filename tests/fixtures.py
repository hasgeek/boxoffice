#!/usr/bin/env python

from boxoffice.models import (db, Item, ItemCollection, DiscountPolicy, DiscountCoupon,
    Price, User, Organization, Category, DISCOUNT_TYPE)
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


def init_data():
    db.drop_all()
    db.create_all()

    user = User(userid=u"U3_JesHfQ2OUmdihAXaAGQ", email=u"test@hasgeek.com")
    db.session.add(user)
    db.session.commit()

    one_month_from_now = date.today() + relativedelta(months=+1)

    rootconf = Organization(title=u'Rootconf', userid=u"U3_JesHfQ2OUmdihAXaAGQ",
        status=0, contact_email=u'test@gmail.com',
        details={'service_tax_no': 'xx', 'address': u'<h2 class="company-name">XYZ</h2> <p>Bangalore - 560034</p> <p>India</p>', 'cin': u'1234', 'pan': u'abc', 'website': u'https://www.test.com', 'refund_policy': u'<p>We offer full refund.</p>', 'support_email': 'test@boxoffice.com', 'ticket_faq': '<p>To cancel your ticket, please mail <a href="mailto:test@boxoffice.com">test@boxoffice.com</a> with your receipt number.</p>'})
    db.session.add(rootconf)
    db.session.commit()

    rc2016 = ItemCollection(title=u'2016', organization=rootconf)
    db.session.add(rc2016)
    db.session.commit()

    category_conference = Category(title=u'Conference', item_collection=rc2016, seq=1)
    db.session.add(category_conference)
    category_workshop = Category(title=u'Workshop', item_collection=rc2016, seq=2)
    db.session.add(category_workshop)
    category_merch = Category(title=u'Merchandise', item_collection=rc2016, seq=3)
    db.session.add(category_merch)
    db.session.commit()

    # import IPython; IPython.embed()
    with db.session.no_autoflush:
        conf_ticket = Item(title=u'Conference ticket', description=u'<p><i class="fa fa-calendar"></i>14 - 15 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>MLR Convention Center, JP Nagar</p><p>This ticket gets you access to rootconf conference on 14th and 15th April 2016.</p>', item_collection=rc2016, category=Category.query.filter_by(name=u'conference').first(), quantity_total=1000)
        rc2016.items.append(conf_ticket)
        db.session.commit()

        expired_ticket = Item(title=u'Expired ticket', description=u'<p><i class="fa fa-calendar"></i>14 - 15 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>MLR Convention Center, JP Nagar</p><p>This ticket gets you access to rootconf conference on 14th and 15th April 2016.</p>', item_collection=rc2016, category=Category.query.filter_by(name=u'conference').first(), quantity_total=1000)
        rc2016.items.append(expired_ticket)
        db.session.commit()

        price = Price(item=conf_ticket, title=u'Super Early Geek', start_at=datetime.utcnow(), end_at=one_month_from_now, amount=3500)
        db.session.add(price)
        db.session.commit()

        single_day_conf_ticket = Item(title=u'Single Day', description=u'<p><i class="fa fa-calendar"></i>14 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>MLR Convention Center, JP Nagar</p><p>This ticket gets you access to rootconf conference on 14th April 2016.</p>', item_collection=rc2016, category=Category.query.filter_by(name=u'conference').first(), quantity_total=1000)
        rc2016.items.append(single_day_conf_ticket)
        db.session.commit()

        single_day_price = Price(item=single_day_conf_ticket, title=u'Single Day', start_at=datetime.utcnow(), end_at=one_month_from_now, amount=2500)
        db.session.add(single_day_price)
        db.session.commit()

        tshirt = Item(title=u'T-shirt', description=u'Rootconf', item_collection=rc2016, category=Category.query.filter_by(name=u'merchandise').first(), quantity_total=1000)
        rc2016.items.append(tshirt)
        db.session.commit()

        tshirt_price = Price(item=tshirt, title=u'T-shirt', start_at=datetime.utcnow(), end_at=one_month_from_now, amount=500)
        db.session.add(tshirt_price)
        db.session.commit()

        dns_workshop = Item(title=u'DNSSEC workshop', description=u'<p><i class="fa fa-calendar"></i>12 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>TERI, Domlur</p><p>This ticket gets you access to DNSSEC workshop 12th April 2016.</p>', item_collection=rc2016, category=Category.query.filter_by(name=u'workshop').first(), quantity_total=1000)
        rc2016.items.append(dns_workshop)
        db.session.commit()

        dns_workshop_price = Price(item=dns_workshop, title=u'DNSSEC workshop early', start_at=datetime.utcnow(), end_at=one_month_from_now, amount=2500)
        db.session.add(dns_workshop_price)
        db.session.commit()

        policy = DiscountPolicy(title=u'10% discount on rootconf', item_quantity_min=10, percentage=10, organization=rootconf)
        policy.items.append(conf_ticket)
        db.session.add(policy)
        db.session.commit()

        tshirt_policy = DiscountPolicy(title=u'5% discount on 5 t-shirts', item_quantity_min=5, percentage=5, organization=rootconf)
        tshirt_policy.items.append(tshirt)
        db.session.add(tshirt_policy)
        db.session.commit()

        discount_coupon1 = DiscountPolicy(title=u'15% discount for coupon code with STU', item_quantity_min=1, percentage=15, organization=rootconf, discount_type=DISCOUNT_TYPE.COUPON)
        discount_coupon1.items.append(conf_ticket)
        db.session.add(discount_coupon1)
        db.session.commit()

        coupon1 = DiscountCoupon(code=u'coupon1', discount_policy=discount_coupon1)
        db.session.add(coupon1)
        db.session.commit()

        discount_coupon_expired_ticket = DiscountPolicy(title=u'15% discount for expired ticket', item_quantity_min=1, percentage=15, organization=rootconf, discount_type=DISCOUNT_TYPE.COUPON)
        discount_coupon_expired_ticket.items.append(expired_ticket)
        db.session.add(discount_coupon_expired_ticket)
        db.session.commit()

        discount_coupon_expired_ticket_coupon = DiscountCoupon(code=u'couponex', discount_policy=discount_coupon_expired_ticket)
        db.session.add(discount_coupon_expired_ticket_coupon)
        db.session.commit()

        discount_coupon2 = DiscountPolicy(title=u'100% discount', item_quantity_min=1, percentage=100, organization=rootconf, discount_type=DISCOUNT_TYPE.COUPON)
        discount_coupon2.items.append(conf_ticket)
        db.session.add(discount_coupon1)
        db.session.commit()

        coupon2 = DiscountCoupon(code=u'coupon2', discount_policy=discount_coupon2)
        db.session.add(coupon2)
        db.session.commit()

        coupon3 = DiscountCoupon(code=u'coupon3', discount_policy=discount_coupon2)
        db.session.add(coupon3)
        db.session.commit()

        forever_early_geek = DiscountPolicy(title=u'Forever Early Geek',
            item_quantity_min=1,
            is_price_based=True,
            discount_type=DISCOUNT_TYPE.COUPON,
            organization=rootconf)
        forever_early_geek.items.append(conf_ticket)
        db.session.add(forever_early_geek)
        db.session.commit()

        forever_coupon = DiscountCoupon(code=u'forever', discount_policy=forever_early_geek)
        db.session.add(forever_coupon)
        db.session.commit()

        noprice_discount = DiscountPolicy(title=u'noprice',
            item_quantity_min=1,
            is_price_based=True,
            discount_type=DISCOUNT_TYPE.COUPON,
            organization=rootconf)
        noprice_discount.items.append(conf_ticket)
        db.session.add(noprice_discount)
        db.session.commit()

        noprice_coupon = DiscountCoupon(code=u'noprice', discount_policy=noprice_discount)
        db.session.add(noprice_coupon)
        db.session.commit()

        forever_unlimited_coupon = DiscountCoupon(code=u'unlimited', discount_policy=forever_early_geek,
            usage_limit=500)
        db.session.add(forever_unlimited_coupon)
        db.session.commit()

        discount_price = Price(item=conf_ticket,
            discount_policy=forever_early_geek, title=u'Forever Early Geek',
            start_at=datetime.utcnow(), end_at=one_month_from_now, amount=3400)
        db.session.add(discount_price)
        db.session.commit()

        unlimited_geek = DiscountPolicy(title=u'Unlimited Geek',
            item_quantity_min=1,
            discount_type=DISCOUNT_TYPE.COUPON,
            percentage=10,
            organization=rootconf)
        unlimited_geek.items.append(conf_ticket)
        db.session.add(unlimited_geek)
        db.session.commit()

        unlimited_coupon = DiscountCoupon(code=u'unlimited', discount_policy=unlimited_geek,
            usage_limit=500)
        db.session.add(unlimited_coupon)
        db.session.commit()

        zero_discount = DiscountPolicy(title=u'Zero Discount',
            item_quantity_min=1,
            is_price_based=True,
            discount_type=DISCOUNT_TYPE.COUPON,
            organization=rootconf)
        zero_discount.items.append(conf_ticket)
        db.session.add(zero_discount)
        db.session.commit()

        zero_coupon = DiscountCoupon(code=u'zerodi', discount_policy=zero_discount)
        db.session.add(zero_coupon)
        db.session.commit()

        zero_discount_price = Price(item=conf_ticket,
            discount_policy=zero_discount, title=u'Zero Discount',
            start_at=datetime.utcnow(), end_at=one_month_from_now, amount=3600)
        db.session.add(zero_discount_price)
        db.session.commit()

        bulk = DiscountPolicy.make_bulk(u'signed', organization=rootconf, title=u'Signed', percentage=10, bulk_coupon_usage_limit=2)
        bulk.items.append(conf_ticket)
        db.session.add(bulk)
        db.session.commit()
