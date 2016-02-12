#!/usr/bin/env python


from boxoffice import init_for
from boxoffice.models import *
init_for('dev')

# try:
db.create_all()
user = User(userid="U3_JesHfQ2OUmdihAXaAGQ")
db.session.add(user)
db.session.commit()

rootconf = Organization(title='Rootconf', userid="U3_JesHfQ2OUmdihAXaAGQ", status=0)
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

conf_ticket = Item(title='Conference ticket', description='Rootconf',  item_collection=rc2016, category=Category.query.filter_by(name='conference').first(), quantity_available=100, quantity_total=1000)
db.session.add(conf_ticket)
db.session.commit()

price = Price(item=conf_ticket, title='Super Early Geek', valid_from='2016-02-01', valid_upto='2016-03-01', amount=3500)
db.session.add(price)
db.session.commit()

single_day_conf_ticket = Item(title='Single Day', description='Rootconf', item_collection=rc2016, category=Category.query.filter_by(name='conference').first(), quantity_available=100, quantity_total=1000)
db.session.add(single_day_conf_ticket)
db.session.commit()

single_day_price = Price(item=single_day_conf_ticket, title='Single Day', valid_from='2016-02-01', valid_upto='2016-03-01', amount=2500)
db.session.add(single_day_price)
db.session.commit()

tshirt = Item(title='T-shirt', description='Rootconf', item_collection=rc2016, category=Category.query.filter_by(name='merchandise').first(), quantity_available=100, quantity_total=1000)
db.session.add(tshirt)
db.session.commit()

tshirt_price = Price(item=tshirt, title='T-shirt', valid_from='2016-02-01', valid_upto='2016-03-01', amount=500)
db.session.add(tshirt_price)
db.session.commit()

dns_workshop = Item(title='DNSSEC workshop', description='Rootconf', item_collection=rc2016, category=Category.query.filter_by(name='workshop').first(), quantity_available=100, quantity_total=1000)
db.session.add(dns_workshop)
db.session.commit()

dns_workshop_price = Price(item=dns_workshop, title='DNSSEC workshop early', valid_from='2016-02-01', valid_upto='2016-03-01', amount=2500)
db.session.add(dns_workshop_price)
db.session.commit()

policy = DiscountPolicy(title='10% discount on rootconf', item_quantity_min=10, item_quantity_max=10, percentage=10, item_collection=rc2016)
policy.items.append(conf_ticket)
db.session.add(policy)
db.session.commit()


tshirt_policy = DiscountPolicy(title='5% discount on 5 t-shirts', item_quantity_min=5, percentage=5, item_collection=rc2016)
policy.items.append(tshirt)
db.session.add(tshirt_policy)
db.session.commit()

coupon = DiscountCoupon(discount_policy=policy, quantity_available=100, quantity_total=100)
db.session.add(coupon)
db.session.commit()

order = Order(user=user, item_collection=rc2016)
db.session.add(order)
db.session.commit()
# except:
#     print "Fail"
#     db.session.rollback()
#     db.drop_all()
