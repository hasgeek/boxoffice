#!/usr/bin/env python


from boxoffice import init_for
from boxoffice.models import *
from coaster.utils import buid
from datetime import date
from dateutil.relativedelta import relativedelta

init_for('dev')

# try:
db.drop_all()
db.create_all()
user = User(userid=buid())
db.session.add(user)
db.session.commit()

one_month_from_now = date.today() + relativedelta(months=+1)

rootconf = Organization(title='Rootconf', userid=user.userid, status=0)
db.session.add(rootconf)
db.session.commit()

rc2016 = ItemCollection(title='2016', organization=rootconf)
db.session.add(rc2016)
db.session.commit()

category_conference = Category(title='Conference', item_collection=rc2016)
db.session.add(category_conference)
category_workshop = Category(title='Workshop', item_collection=rc2016)
db.session.add(category_workshop)
category_merch = Category(title='Merchandise', item_collection=rc2016)
db.session.add(category_merch)
db.session.commit()

conf_ticket = Item(title='Conference ticket', description='<p><i class="fa fa-calendar"></i>14 - 15 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>MLR Convention Center, JP Nagar</p><p>This ticket gets you access to rootconf conference on 14th and 15th April 2016.</p>',  item_collection=rc2016, category=Category.query.filter_by(name='conference').first(), quantity_available=100, quantity_total=1000)
db.session.add(conf_ticket)
db.session.commit()

price = Price(item=conf_ticket, title='Super Early Geek', valid_from=date.today(), valid_upto=one_month_from_now, amount=3500)
db.session.add(price)
db.session.commit()

single_day_conf_ticket = Item(title='Single Day 1', description='<p><i class="fa fa-calendar"></i>14 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>MLR Convention Center, JP Nagar</p><p>This ticket gets you access to rootconf conference on 14th April 2016.</p>', item_collection=rc2016, category=Category.query.filter_by(name='conference').first(), quantity_available=100, quantity_total=1000)
db.session.add(single_day_conf_ticket)
db.session.commit()

single_day_price = Price(item=single_day_conf_ticket, title='Single Day', valid_from=date.today(), valid_upto=one_month_from_now, amount=2500)
db.session.add(single_day_price)
db.session.commit()

single_day2_conf_ticket = Item(title='Single Day 2', description='<p><i class="fa fa-calendar"></i>15 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>MLR Convention Center, JP Nagar</p><p>This ticket gets you access to rootconf conference on 15th April 2016.</p>', item_collection=rc2016, category=Category.query.filter_by(name='conference').first(), quantity_available=100, quantity_total=1000)
db.session.add(single_day2_conf_ticket)
db.session.commit()

single_day2_price = Price(item=single_day2_conf_ticket, title='Single Day', valid_from=date.today(), valid_upto=one_month_from_now, amount=2500)
db.session.add(single_day2_price)
db.session.commit()

tshirt = Item(title='T-shirt', description='Rootconf conference T-shirt', item_collection=rc2016, category=Category.query.filter_by(name='merchandise').first(), quantity_available=100, quantity_total=1000)
db.session.add(tshirt)
db.session.commit()

tshirt_price = Price(item=tshirt, title='Regular', valid_from=date.today(), valid_upto=one_month_from_now, amount=500)
db.session.add(tshirt_price)
db.session.commit()

dns_workshop = Item(title='DNSSEC workshop', description='<p><i class="fa fa-calendar"></i>12 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>TERI, Domlur</p><p>This ticket gets you access to DNSSEC workshop 12th April 2016.</p>', item_collection=rc2016, category=Category.query.filter_by(name='workshop').first(), quantity_available=100, quantity_total=1000)
db.session.add(dns_workshop)
db.session.commit()

dns_workshop_price = Price(item=dns_workshop, title='Early Geek', valid_from=date.today(), valid_upto=one_month_from_now, amount=2500)
db.session.add(dns_workshop_price)
db.session.commit()

policy = DiscountPolicy(title='10% discount on 10 or more tickets', item_quantity_min=10, percentage=10, organization=rootconf)
policy.items.append(conf_ticket)
db.session.add(policy)
db.session.commit()

policy2 = DiscountPolicy(title='5% discount on 5 or more tickets', item_quantity_min=5, percentage=5, organization=rootconf)
policy2.items.append(conf_ticket)
db.session.add(policy2)
db.session.commit()

tshirt_policy = DiscountPolicy(title='5% discount on 5 or more t-shirts', item_quantity_min=5, percentage=5, organization=rootconf)
tshirt_policy.items.append(tshirt)
db.session.add(tshirt_policy)
db.session.commit()

discount_coupon1 = DiscountPolicy(title='15% discount for coupon code with STU', item_quantity_min=1, item_quantity_max=1, percentage=15, organization=rootconf, discount_type=DISCOUNT_TYPE.COUPON)
discount_coupon1.items.append(conf_ticket)
db.session.add(discount_coupon1)
db.session.commit()

coupon = DiscountCoupon(code='xyzer', discount_policy=discount_coupon1, quantity_available=100, quantity_total=100)
db.session.add(coupon)
db.session.commit()

speaker_discount = DiscountPolicy(title='100% discount for speaker coupons', item_quantity_min=1, item_quantity_max=1, percentage=100, organization=rootconf, discount_type=DISCOUNT_TYPE.COUPON)
speaker_discount.items.append(conf_ticket)
db.session.add(speaker_discount)
db.session.commit()

speaker1 = DiscountCoupon(code='speaker1', discount_policy=speaker_discount, quantity_available=1, quantity_total=1)
db.session.add(speaker1)
db.session.commit()

speaker2 = DiscountCoupon(code='speaker2', discount_policy=speaker_discount, quantity_available=1, quantity_total=1)
db.session.add(speaker2)
db.session.commit()

discount_coupon2 = DiscountPolicy(title='20% discount for workshop ticket', item_quantity_min=1, item_quantity_max=1, percentage=20, organization=rootconf, discount_type=DISCOUNT_TYPE.COUPON)
discount_coupon2.items.append(dns_workshop)
db.session.add(discount_coupon2)
db.session.commit()

coupon1 = DiscountCoupon(code='wert34', discount_policy=discount_coupon2, quantity_available=100, quantity_total=100)
db.session.add(coupon1)
db.session.commit()





