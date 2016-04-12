from boxoffice import app
from boxoffice.models import ItemCollection, LineItem, Order, ORDER_STATUS
import requests
import json
from tabulate import tabulate
from rq.decorators import job


def tabulate_stats(item_collection):
    started = [ORDER_STATUS.PURCHASE_ORDER]
    sold = [ORDER_STATUS.SALES_ORDER, ORDER_STATUS.INVOICE]
    cancelled = [ORDER_STATUS.CANCELLED]
    results = []
    for item in item_collection.items:
        initiated_line_items = LineItem.query.join(Order).filter(LineItem.item == item, Order.status.in_(started)).count()

        sold_line_items = LineItem.query.join(Order).filter(LineItem.item == item, Order.status.in_(sold)).count()

        cancelled_line_items = LineItem.query.join(Order).filter(LineItem.item == item, Order.status.in_(cancelled)).count()

        results.append([item.title, initiated_line_items, sold_line_items, cancelled_line_items])
    return tabulate(results, headers=["Ticket", "Initiated", "Sold", "Cancelled"])


@job('boxoffice')
def post_stats(id, webhook_url):
    with app.test_request_context():
        item_collection = ItemCollection.query.get(id)
        table = tabulate_stats(item_collection)
        stats = ":moneybag: " + item_collection.title + "\n```" + table + "```"
        data = {"username": "boxoffice", "text": stats}
        response = requests.post(webhook_url, data=json.dumps(data))

        # TODO: Debug error code, maybe retry?
        if response.status_code != 200:
            pass
