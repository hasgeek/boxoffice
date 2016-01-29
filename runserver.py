#!/usr/bin/env python
from boxoffice import app, init_for, models
from boxoffice.models import *
init_for('dev')
db.create_all()

# Seed with sample data
with app.test_request_context():

    if False:  # change to false to reset database
        db.drop_all()
        db.session.commit()
        db.create_all()

        hg = Organization(title="HasGeek", userid="U3_JesHfQ2OUmdihAXaAGQ", status=0)
        db.session.add(hg)
        db.session.commit()

        category_merch = Category(title='Merch', organization=hg)
        db.session.add(category_merch)
        category_conference = Category(title='Conference', organization=hg)
        db.session.add(category_conference)
        db.session.commit()

        event = Event(title='Rootconf', organization=hg)
        db.session.add(event)
        db.session.commit()

        item = Item(title='Rootconf Conference', description='Rootconf', organization=hg, category=Category.query.filter_by(name='conference').first(), quantity_available=100, quantity_total=1000, events=Event.query.all())
        db.session.add(item)
        db.session.commit()

        price = Price(item=item, title='Super Early Geek', valid_from='2016-02-01', valid_upto='2016-03-01', amount=3500)
        db.session.add(price)
        db.session.commit()

        policy = DiscountPolicy(title='10% discount on rootconf', quantity_from=1, quantity_to=1, percentage=10)
        policy.items.append(item)
        db.session.add(policy)
        db.session.commit()

        coupon = DiscountCoupon(discount_policy=policy, quantity_available=100, quantity_total=100)
        db.session.add(coupon)
        db.session.commit()

app.run('0.0.0.0', 6500, debug=True)
