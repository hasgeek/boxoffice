from flask import jsonify
from .. import app, lastuser
from sqlalchemy import func
from coaster.views import load_models, render_with
from boxoffice.models import db, ItemCollection, LineItem, LINE_ITEM_STATUS


def jsonify_item(item):
    sold = LineItem.query.filter(LineItem.item == item, LineItem.final_amount > 0, LineItem.status == LINE_ITEM_STATUS.CONFIRMED).count()
    free = LineItem.query.filter(LineItem.item == item, LineItem.final_amount == 0, LineItem.status == LINE_ITEM_STATUS.CONFIRMED).count()
    cancelled = LineItem.query.filter(LineItem.item == item, LineItem.status == LINE_ITEM_STATUS.CANCELLED).count()
    available = item.quantity_total - (sold + free - cancelled)
    net_sales = db.session.query(func.sum(LineItem.final_amount)).filter(LineItem.item == item, LineItem.status == LINE_ITEM_STATUS.CONFIRMED).first()
    return {
        'id': item.id,
        'title': item.title,
        'available': available,
        'sold': sold,
        'free': free,
        'cancelled': cancelled,
        'current_price': item.current_price().amount if item.current_price() else "No active price",
        'net_sales': net_sales[0] if net_sales[0] else 0
    }


def jsonify_item_collection(item_collection_dict):
    item_ids = [item.id for item in item_collection_dict['item_collection'].items]
    net_sales = db.session.query(func.sum(LineItem.final_amount)).filter(LineItem.item_id.in_(item_ids), LineItem.status == LINE_ITEM_STATUS.CONFIRMED).first()
    return jsonify(items=[jsonify_item(item)
        for item in item_collection_dict['item_collection'].items],
        date_item_counts=item_collection_dict['date_item_counts'],
        date_sales=item_collection_dict['date_sales'],
        net_sales=net_sales[0] if net_sales[0] else 0)


@app.route('/admin/ic/<ic_id>')
@lastuser.requires_login
@load_models(
    (ItemCollection, {'id': 'ic_id'}, 'item_collection'),
    )
@render_with({'text/html': 'index.html', 'application/json': jsonify_item_collection}, json=True)
def admin_item_collection(item_collection):
    date_item_counts = LineItem.counts_per_date_per_item(item_collection)
    date_sales = LineItem.sales_by_date(date_item_counts.keys())
    return dict(item_collection=item_collection, date_item_counts=date_item_counts, date_sales=date_sales)
