from boxoffice import app
from boxoffice.models import DiscountPolicy, ItemCollection, LineItem, Order, ORDER_STATUS
from boxoffice.models.line_item import LINE_ITEM_STATUS
import requests
import json
from tabulate import tabulate
from rq.decorators import job

# def discount_stats(item_collection):
#     stats = []
#     for policy in DiscountPolicy.query.get(item_collection):
#         line_item_count = line_item_count=LineItem.query.filter(LineItem.item_id.in_([li_item.id for li_item in policy.items]), LineItem.status==LINE_ITEM_STATUS.CONFIRMED, LineItem.discount_policy == policy).count()
#         stats.append([policy.title, line_item_count])
#     return tabulate(stats, headers=["Policy Title", "Count"])

def ticket_stats(item_collection):
    started = [ORDER_STATUS.PURCHASE_ORDER]
    sold = [ORDER_STATUS.SALES_ORDER, ORDER_STATUS.INVOICE]
    cancelled = [ORDER_STATUS.CANCELLED]
    stats = []
    for item in item_collection.items:
        initiated_line_items = LineItem.query.join(Order).filter(LineItem.item == item, Order.status.in_(started)).count()

        sold_line_items = LineItem.query.join(Order).filter(LineItem.item == item, Order.status.in_(sold), LineItem.status==LINE_ITEM_STATUS.CONFIRMED).count()

        cancelled_line_items = LineItem.query.filter(LineItem.item == item, LineItem.status==LINE_ITEM_STATUS.CANCELLED).count()

        stats.append([item.title, initiated_line_items, sold_line_items, cancelled_line_items])
    return tabulate(stats, headers=["Ticket", "Initiated", "Sold", "Cancelled"])

@job('boxoffice')
def post_stats(id, webhook_url):
    with app.test_request_context():
        item_collection = ItemCollection.query.get(id)
        tickets = ticket_stats(item_collection)
        stats = ":moneybag: " + item_collection.title + "\n```" + tickets + "```"
        data = {"username": "boxoffice", "text": stats}
        response = requests.post(webhook_url, data=json.dumps(data))

        # TODO: Debug error code, maybe retry?
        if response.status_code != 200:
            pass
