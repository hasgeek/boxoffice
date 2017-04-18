from boxoffice import init_for
from boxoffice.models import ItemCollection, LineItem, Order, ORDER_STATUS
from datetime import datetime as dt
from os import environ
import requests
from urllib import urlencode
import json
from tabulate import tabulate

def get_stats():
    """ Query development database for stats on a particular ItemCollection """
    init_for('dev')
    item_collection =  ItemCollection.query.get(environ.get('ITEM_COLLECTION_ID'))
    started = [ORDER_STATUS.PURCHASE_ORDER]
    sold = [ORDER_STATUS.SALES_ORDER, ORDER_STATUS.INVOICE]
    cancelled = [ORDER_STATUS.CANCELLED]
    results = []
    for item in item_collection.items:
        results.append([item.title, LineItem.query.join(Order).filter(LineItem.item == item, Order.status.in_(started)).count(), LineItem.query.join(Order).filter(LineItem.item == item, Order.status.in_(sold)).count(), LineItem.query.join(Order).filter(LineItem.item == item, Order.status.in_(cancelled)).count()])
    # Prepend and append tilde for the stats to be published with raw text highlighting
    stats = "```" + tabulate(results, headers=["Event","Initiated", "Sold", "Cancelled"]) + "```"
    return stats

def post_stats(stats):
    """
    Post stats to #customersupport via Slack WEBHOOK_URL
    """
    data={"channel": "#customersupport", "username": "boxoffice-stats", "icon_emoji": ":moneybag:", "text": stats}
    response = requests.post(environ.get('WEBHOOK_URL'), data = json.dumps(data))
    if response.status_code == 200:
        print "Posted! ", dt.utcnow()
    else:
        print "Oops!" + response.status_code

post_stats(get_stats())
