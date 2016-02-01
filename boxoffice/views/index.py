from pytz import utc, timezone
from boxoffice import app
from flask import redirect, url_for, render_template, request
from coaster.views import load_models, jsonp

from boxoffice.models import Organization, Item, Category, Event

#U3_JesHfQ2OUmdihAXaAGQ


def item_json(item):
    return {
        'title': item.title,
        'id': item.id,
        'description': item.description,
        'quantity_available': item.quantity_available,
        'quantity_total': item.quantity_total,
        'category_id': item.category_id,
        'organization_id': item.organization_id,
        'price': "3500"
    }


def category_json(category, items):
    return {
        'id': category.id,
        'title': category.title,
        'organization_id': category.organization_id,
        'items': [item_json(i) for i in items]
    }


def event_json(event):
    return {
        'title': event.title,
        'website': event.website,
        'funnel_link': event.funnel_link,
        'organization_id': event.organization_id,
        'items': [i.id for i in event.items]
    }


@app.route('/')
def index():
    return render_template('ticketing.html')


@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='img/favicon.ico'), code=301)


@app.route('/items.json')
def temp_items():
    return render_template('items.json')


@app.route('/<organization>/inventory')
@load_models(
    (Organization, {'name': 'organization'}, 'organization'),
    )
def get_inventory(organization):
    print "Hello"
    eventsargs = request.args.getlist('events')
    events = Event.query.filter(Event.name.in_(eventsargs))
    items = organization.items
    categories = organization.categories
    return jsonp(**{
        'html': render_template('boxoffice.html'),
        'categories': [category_json(c, Item.query.filter_by(category=c)) for c in categories],
        'events': [event_json(e) for e in events]
        })


@app.template_filter('shortdate')
def shortdate(date):
    tz = timezone(app.config['TIMEZONE'])
    return utc.localize(date).astimezone(tz).strftime('%b %e')


@app.template_filter('longdate')
def longdate(date):
    tz = timezone(app.config['TIMEZONE'])
    return utc.localize(date).astimezone(tz).strftime('%B %e, %Y')
