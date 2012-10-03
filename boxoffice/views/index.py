from pytz import utc, timezone
from flask import render_template, g
from coaster.views import load_model
from boxoffice import app
from flask import render_template, redirect, url_for

from boxoffice.models.category import Category, CATEGORY_STATUS
from boxoffice.models.event import Event
from boxoffice.views.login import lastuser, requires_workspace_member

@app.context_processor
def sidebarvars():
    return {
            'permissions': lastuser.permissions()
    }

@app.route('/')
def index():
    events = Event.query.order_by('title').all()
    live_categories = Category.get_by_status(status=CATEGORY_STATUS.LIVE)
    return render_template('index.html', events=events, live_categories=live_categories)


@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='img/favicon.ico'), code=301)


@app.template_filter('shortdate')
def shortdate(date):
    tz = timezone(app.config['TIMEZONE'])
    return utc.localize(date).astimezone(tz).strftime('%b %e')


@app.template_filter('longdate')
def longdate(date):
    tz = timezone(app.config['TIMEZONE'])
    return utc.localize(date).astimezone(tz).strftime('%B %e, %Y')



    