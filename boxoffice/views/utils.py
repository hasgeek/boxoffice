# -*- coding: utf-8 -*-

import datetime
from pytz import utc, timezone
from flask import request, abort, Response, jsonify, make_response
from functools import wraps
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import unicodecsv
from baseframe import localize_timezone
from boxoffice import app


def xhr_only(f):
    """Aborts if a request does not have the XMLHttpRequest header set"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.method != 'OPTIONS' and not request.is_xhr:
            abort(400)
        return f(*args, **kwargs)
    return wrapper


def check_api_access(access_token):
    """Aborts if a request does not have the correct access token"""
    if not request.args.get('access_token') or request.args.get('access_token') != access_token:
        abort(401)


@app.template_filter('date_time_format')
def date_time_format(datetime):
    return localize_timezone(datetime).strftime('%d %b %Y %H:%M:%S')


@app.template_filter('date_format')
def date_format(datetime):
    return localize_timezone(datetime).strftime('%d %b %Y')


def localize(datetime, tz):
    return utc.localize(datetime).astimezone(timezone(tz))


@app.template_filter('invoice_date')
def invoice_date_filter(date, format):
    return localize(date, app.config['TIMEZONE']).strftime(format)


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


def csv_response(headers, rows, row_handler=None):
    """
    Returns a response, with mimetype set to text/csv,
    given a list of headers and a two-dimensional list of rows

    Accepts an optional row_handler function that can be used to transform the row. The row
    must be a list or a tuple of values.
    """
    stream = StringIO()
    csv_writer = unicodecsv.writer(stream)
    csv_writer.writerow(headers)
    if callable(row_handler):
        csv_writer.writerows(row_handler(row) for row in rows)
    else:
        csv_writer.writerows(rows)
    return Response(unicode(stream.getvalue()), content_type='text/csv')


def api_error(message, status_code):
    """
    Generates a HTTP response as a JSON object for a failure scenario

    :param string message: Error message to be included as part of the JSON response
    :param int status_code: HTTP status code to be used for the response
    """
    return make_response(jsonify(status='error', message=message), status_code)


def api_success(result, doc, status_code):
    """
    Generates a HTTP response as a JSON object for a successful scenario

    :param any result: Top-level data to be encoded as JSON
    :param string doc: Documentation to be included as part of the JSON response
    :param int status_code: HTTP status code to be used for the response
    """
    return make_response(jsonify(status='ok', doc=doc, result=result), status_code)
