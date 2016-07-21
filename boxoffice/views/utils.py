# -*- coding: utf-8 -*-

from pytz import utc, timezone
from flask import request, abort
from functools import wraps
from boxoffice import app


def xhr_only(f):
    """
    Aborts if a request does not have the XMLHttpRequest header set
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.method != 'OPTIONS' and not request.is_xhr:
            abort(400)
        return f(*args, **kwargs)
    return wrapper


def localize(datetime, tz):
    return utc.localize(datetime).astimezone(timezone(tz))


@app.template_filter('date_time_format')
def date_time_format(datetime):
    return utc.localize(datetime).astimezone(timezone(app.config['TIMEZONE'])).strftime('%d %b %Y %H:%M:%S')


@app.template_filter('date_format')
def date_format(datetime):
    return utc.localize(datetime).astimezone(timezone(app.config['TIMEZONE'])).strftime('%d %b %Y')


def cors(f):
    """
    Adds CORS headers to the decorated view function.

    Requires `app.config['ALLOWED_ORIGINS']` to be defined with a list
    of permitted domains. Eg: app.config['ALLOWED_ORIGINS'] = ['https://example.com']
    """
    def add_headers(resp, origin):
        resp.headers['Access-Control-Allow-Origin'] = origin
        resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS, GET'
        # echo the request's headers
        resp.headers['Access-Control-Allow-Headers'] = request.headers.get('Access-Control-Request-Headers')
        # debugging only
        if app.debug:
            resp.headers['Access-Control-Max-Age'] = '1'
        return resp

    @wraps(f)
    def wrapper(*args, **kwargs):
        origin = request.headers.get('Origin')
        if not origin or origin not in app.config['ALLOWED_ORIGINS']:
            abort(401)

        if request.method == 'OPTIONS':
            # pre-flight request, check CORS headers directly
            resp = app.make_default_options_response()
        else:
            resp = f(*args, **kwargs)
        return add_headers(resp, origin)

    return wrapper
