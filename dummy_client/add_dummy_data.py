from boxoffice import init_for, app, db
from boxoffice.models import Organization, Category, Item, Price, ItemCollection, LineItem, Order, ORDER_STATUS
from coaster.utils import buid
import datetime as dt
import pytz

def convert_to_utc(localtime, tz="Asia/Calcutta", is_dst=True):
    local = pytz.timezone(tz)
    local_dt = local.localize(localtime, is_dst=is_dst)
    return local_dt.astimezone(pytz.UTC).replace(tzinfo=None)

# Seed with sample data:
with app.app_context():
    init_for('dev')
    dummy_org = Organization(title=u'Dummy Org', contact_email=u'dummy@dummy.org', userid=buid(), status=0, details={'service_tax_no': u'ABCDEFGHIJKLMNO', 'address': u'<h2 class=u"company-name">Dummy LLP</h2> <p>10</p> <p>Downing Street</p> <p>London - SW1A 2AA</p> <p>England</p>', 'cin': u'123456789101112131516', 'pan': u'12345678910'})
    db.session.add(dummy_org)
    dummy_event = ItemCollection(title='dummy-2016', organization=dummy_org)
    db.session.add(dummy_event)

    dummy_category = Category(title='Category', item_collection=dummy_event, seq=1)
    db.session.add(dummy_category)

    dummy_item = Item(title=u'Dummy Ticket', description=u'<p><i class="fa fa-calendar"></i>1 - 2 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>10 Downing Street</p><p>Blah blah</p>', item_collection=dummy_event, category=dummy_category, quantity_available=10, quantity_total=10)
    db.session.add(dummy_item)

    dummy_price = Price(item=dummy_item, title=u'Early Geek', start_at=convert_to_utc(dt.datetime.now()), end_at=convert_to_utc(dt.datetime.now()+dt.timedelta(25,5)), amount=100)
    db.session.add(dummy_price)
    db.session.commit()
