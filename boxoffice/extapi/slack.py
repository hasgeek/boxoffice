from boxoffice import db, app
from boxoffice.models import ItemCollection, LineItem, Order, ORDER_STATUS
from datetime import datetime as dt
import requests
from urllib import urlencode
import json
from tabulate import tabulate
from rq.decorators import job

@job('boxoffice')
def post_stats(id, webhook_url):
    with app.test_request_context():
        item_collection =  ItemCollection.query.get(id)
        started = [ORDER_STATUS.PURCHASE_ORDER]
        sold = [ORDER_STATUS.SALES_ORDER, ORDER_STATUS.INVOICE]
        cancelled = [ORDER_STATUS.CANCELLED]
        results = []
        for item in item_collection.items:
            initiated_line_items = LineItem.query.join(Order).filter(LineItem.item == item, Order.status.in_(started)).count()
            sold_line_items = LineItem.query.join(Order).filter(LineItem.item == item, Order.status.in_(sold)).count()
            cancelled_line_items = LineItem.query.join(Order).filter(LineItem.item == item, Order.status.in_(cancelled)).count()
            results.append([initiated_line_items, sold_line_items, cancelled_line_items])
        stats = ":moneybag: " + "```" + tabulate(results, headers = ["Event", "Initiated", "Sold", "Cancelled"]) + "```"
        data = {"username": "boxoffice", "text": stats}
        response = requests.post(webhook_url, data = json.dumps(data))
