# -*- coding: utf-8 -*-

from flask import request, abort, Response, jsonify, make_response
from functools import wraps
from urlparse import urlparse
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


def check_api_access(api_token):
    """Aborts if a request does not have the correct api_token"""
    if not request.args.get('api_token') or request.args.get('api_token') != api_token:
        abort(401)


def json_date_format(dt):
    return localize_timezone(dt).isoformat()


@app.template_filter('longdate')
def longdate(date):
    return localize_timezone(date).strftime('%e %B %Y')


def basepath(url):
    """
    Returns the base path of a given a URL
    Eg::

        basepath("https://hasgeek.com/1")
        >> u"https://hasgeek.com

    :param url: A valid URL unicode string. Eg: https://hasgeek.com
    """
    parsed_url = urlparse(url)
    if not (parsed_url.scheme or parsed_url.netloc):
        raise ValueError("Invalid URL")
    return u"{scheme}://{netloc}".format(scheme=parsed_url.scheme, netloc=parsed_url.netloc)


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
        if not origin:
            # Firefox doesn't send the Origin header, so read the Referer header instead
            # TODO: Remove this conditional when Firefox starts adding an Origin header
            referer = request.referrer
            if referer:
                origin = basepath(referer)

        if request.method == 'POST' and not origin or origin not in app.config['ALLOWED_ORIGINS']:
            abort(401)

        if request.method == 'OPTIONS':
            # pre-flight request, check CORS headers directly
            resp = app.make_default_options_response()
        else:
            resp = f(*args, **kwargs)
        return add_headers(resp, origin)

    return wrapper


def csv_response(headers, rows, row_type=None, row_handler=None):
    """
    Returns a response, with mimetype set to text/csv,
    given a list of headers and a two-dimensional list of rows

    The default type of row is a list or a tuple of values. If row is of type dict set the row_type.

    Accepts an optional row_handler function that can be used to transform the row.
    """
    stream = StringIO()
    if row_type == 'dict':
        csv_writer = unicodecsv.DictWriter(stream, fieldnames=headers, extrasaction='ignore')
        csv_writer.writeheader()
    else:
        csv_writer = unicodecsv.writer(stream)
        csv_writer.writerow(headers)
    if callable(row_handler):
        csv_writer.writerows(row_handler(row) for row in rows)
    else:
        csv_writer.writerows(rows)
    return Response(unicode(stream.getvalue()), mimetype='text/csv')


def api_error(message, status_code, errors=[]):
    """
    Generates a HTTP response as a JSON object for a failure scenario

    :param string message: Human readable error message to be included as part of the JSON response
    :param string message: Error message to be included as part of the JSON response
    :param list errors: Error messages to be included as part of the JSON response
    :param int status_code: HTTP status code to be used for the response
    """
    return make_response(jsonify(status='error', errors=errors, message=message), status_code)


def api_success(result, doc, status_code):
    """
    Generates a HTTP response as a JSON object for a successful scenario

    :param any result: Top-level data to be encoded as JSON
    :param string doc: Documentation to be included as part of the JSON response
    :param int status_code: HTTP status code to be used for the response
    """
    return make_response(jsonify(status='ok', doc=doc, result=result), status_code)
