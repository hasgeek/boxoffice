from pytz import utc, timezone
from boxoffice import app
from flask import redirect, url_for, render_template, request
from coaster.views import load_models, jsonp

from boxoffice.models import Organization, Item, Category, Event

#U3_JesHfQ2OUmdihAXaAGQ


@app.route('/')
def index():
    return render_template('ticketing.html')


@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='img/favicon.ico'), code=301)


@app.route('/items.json')
def temp_items():
    return render_template('items.json')


@app.route('/<organization>/inventory', methods=['GET'])
@load_models(
    (Organization, {'buid': 'organization'}, 'organization'),
    )
def get_inventory(organization):
    eventsargs = request.args.getlist('events')
    events = Event.query.filter(Event.name.in_(eventsargs))
    items = Item.query.filter_by(organization=organization)
    categories = Category.query.filter_by(organization=organization)
    return jsonp(**{
        'items': [i for i in items],
        'categories': [c for c in categories],
        'events': [e for e in events]
        })


@app.template_filter('shortdate')
def shortdate(date):
    tz = timezone(app.config['TIMEZONE'])
    return utc.localize(date).astimezone(tz).strftime('%b %e')


@app.template_filter('longdate')
def longdate(date):
    tz = timezone(app.config['TIMEZONE'])
    return utc.localize(date).astimezone(tz).strftime('%B %e, %Y')
