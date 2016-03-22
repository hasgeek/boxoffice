#!/usr/bin/env python

from boxoffice.models import *
from datetime import date
from dateutil.relativedelta import relativedelta
from coaster.utils import buid

class Fixtures(object):
    def make_fixtures(self):
        """
        Create test fixtures
        """
        user = User(userid=buid(), email=u"test@hasgeek.com")
        db.session.add(user)
        db.session.commit()

        one_month_from_now = date.today() + relativedelta(months=+1)

        rootconf = Organization(title=u'Rootconf', userid=u"U3_JesHfQ2OUmdihAXaAGQ",
            status=0, contact_email=u'test@gmail.com',
            details={'service_tax_no': u'xx', 'address': u'<h2 class="company-name">XYZ</h2> <p>Bangalore - 560034</p> <p>India</p>', 'cin': u'1234', 'pan': u'abc', 'website': u'https://www.test.com'})
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

        conf_ticket = Item(title=u'Conference ticket', description=u'<p><i class="fa fa-calendar"></i>14 - 15 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>MLR Convention Center, JP Nagar</p><p>This ticket gets you access to rootconf conference on 14th and 15th April 2016.</p>',  item_collection=rc2016, category=Category.query.filter_by(name=u'conference').first(), quantity_available=100, quantity_total=1000)
        db.session.add(conf_ticket)
        db.session.commit()

        price = Price(item=conf_ticket, title=u'Super Early Geek', start_at=date.today(), end_at=one_month_from_now, amount=3500)
        db.session.add(price)
        db.session.commit()

        single_day_conf_ticket = Item(title=u'Single Day', description=u'<p><i class="fa fa-calendar"></i>14 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>MLR Convention Center, JP Nagar</p><p>This ticket gets you access to rootconf conference on 14th April 2016.</p>', item_collection=rc2016, category=Category.query.filter_by(name=u'conference').first(), quantity_available=100, quantity_total=1000)
        db.session.add(single_day_conf_ticket)
        db.session.commit()

        single_day_price = Price(item=single_day_conf_ticket, title=u'Single Day', start_at=date.today(), end_at=one_month_from_now, amount=2500)
        db.session.add(single_day_price)
        db.session.commit()

        tshirt = Item(title=u'T-shirt', description=u'Rootconf', item_collection=rc2016, category=Category.query.filter_by(name=u'merchandise').first(), quantity_available=100, quantity_total=1000)
        db.session.add(tshirt)
        db.session.commit()

        tshirt_price = Price(item=tshirt, title=u'T-shirt', start_at=date.today(), end_at=one_month_from_now, amount=500)
        db.session.add(tshirt_price)
        db.session.commit()

        dns_workshop = Item(title=u'DNSSEC workshop', description=u'<p><i class="fa fa-calendar"></i>12 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>TERI, Domlur</p><p>This ticket gets you access to DNSSEC workshop 12th April 2016.</p>', item_collection=rc2016, category=Category.query.filter_by(name=u'workshop').first(), quantity_available=100, quantity_total=1000)
        db.session.add(dns_workshop)
        db.session.commit()

        dns_workshop_price = Price(item=dns_workshop, title=u'DNSSEC workshop early', start_at=date.today(), end_at=one_month_from_now, amount=2500)
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

        discount_coupon1 = DiscountPolicy(title=u'15% discount for coupon code with STU', item_quantity_min=1, item_quantity_max=1, percentage=15, organization=rootconf, discount_type=DISCOUNT_TYPE.COUPON)
        discount_coupon1.items.append(conf_ticket)
        db.session.add(discount_coupon1)
        db.session.commit()

        coupon1 = DiscountCoupon(code=u'coupon1', discount_policy=discount_coupon1, quantity_available=100, quantity_total=100)
        db.session.add(coupon1)
        db.session.commit()

        discount_coupon2 = DiscountPolicy(title=u'100% discount', item_quantity_min=1, item_quantity_max=1, percentage=100, organization=rootconf, discount_type=DISCOUNT_TYPE.COUPON)
        discount_coupon2.items.append(conf_ticket)
        db.session.add(discount_coupon1)
        db.session.commit()

        coupon2 = DiscountCoupon(code=u'coupon2', discount_policy=discount_coupon2, quantity_available=100, quantity_total=100)
        db.session.add(coupon2)
        db.session.commit()

        coupon3 = DiscountCoupon(code=u'coupon3', discount_policy=discount_coupon2, quantity_available=100, quantity_total=100)
        db.session.add(coupon3)
        db.session.commit()
