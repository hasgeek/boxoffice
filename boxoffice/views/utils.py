import csv
from collections.abc import Callable, Sequence
from datetime import datetime
from functools import wraps
from io import StringIO
from typing import Any, Literal, ParamSpec, TypeVar, overload
from urllib.parse import urlparse

from flask import Response, abort, after_this_request, make_response, request
from flask.typing import ResponseReturnValue
from werkzeug.wrappers import Response as BaseResponse

from baseframe import localize_timezone, request_is_xhr

from .. import app

_R_co = TypeVar('_R_co', covariant=True)
_P = ParamSpec('_P')


def sanitize_coupons(coupons: Any) -> list[str]:
    if not isinstance(coupons, list):
        return []
    # Remove falsy values and coerce the valid values into unicode
    return [str(coupon_code) for coupon_code in coupons if coupon_code]


def vary_accept(response: Response) -> Response:
    """Vary request on the Accept header."""
    response.vary.add('Accept')
    return response


def request_wants_json() -> bool:
    """Request wants a JSON response."""
    after_this_request(vary_accept)
    return request.accept_mimetypes.best == 'application/json'


def xhr_only(f: Callable[_P, _R_co]) -> Callable[_P, _R_co]:
    """Abort if a request does not have the XMLHttpRequest header set."""

    @wraps(f)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R_co:
        if request.method != 'OPTIONS' and not request_is_xhr():
            abort(400)
        return f(*args, **kwargs)

    return wrapper


def check_api_access(api_token: Any | None) -> None:
    """Abort if a request does not have the correct api_token."""
    if not request.args.get('api_token') or request.args.get('api_token') != api_token:
        abort(401)


@overload
def json_date_format(dt: None) -> None: ...


@overload
def json_date_format(dt: datetime) -> str: ...


def json_date_format(dt: datetime | None) -> str | None:
    if dt is not None:
        return localize_timezone(dt).isoformat()
    return None


@app.template_filter('longdate')
def longdate(date: datetime) -> str:
    return localize_timezone(date).strftime('%e %B %Y')


def basepath(url: str) -> str:
    """
    Return the base path of a given URL.

    Eg::

        basepath("https://hasgeek.com/1")
        >> u"https://hasgeek.com

    :param url: A valid URL unicode string. Eg: https://hasgeek.com
    """
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValueError(f"URL is missing scheme or netloc: {url}")
    return f'{parsed_url.scheme}://{parsed_url.netloc}'


# TODO: Replace this with Coaster's `@cors` decorator
def cors(f: Callable[_P, ResponseReturnValue]) -> Callable[_P, BaseResponse]:
    """
    Add CORS headers to the decorated view function.

    Requires `app.config['ALLOWED_ORIGINS']` to be defined with a list
    of permitted domains. Eg: app.config['ALLOWED_ORIGINS'] = ['https://example.com']
    """

    def add_headers(resp: BaseResponse, origin: str) -> BaseResponse:
        resp.headers['Access-Control-Allow-Origin'] = origin
        resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS, GET'
        # echo the request's headers
        if allow_headers := request.headers.get('Access-Control-Request-Headers'):
            resp.headers['Access-Control-Allow-Headers'] = allow_headers
        # debugging only
        if app.debug:
            resp.headers['Access-Control-Max-Age'] = '1'
        return resp

    @wraps(f)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> BaseResponse:
        origin = request.headers.get('Origin')
        if not origin:
            # Firefox doesn't send the Origin header in some contexts, so read the
            # Referrer header instead.
            # https://wiki.mozilla.org/Security/Origin#Privacy-Sensitive_Contexts
            referrer = request.referrer
            origin = basepath(referrer) if referrer else 'null'

        if (request.method == 'POST' and not origin) or origin not in app.config[
            'ALLOWED_ORIGINS'
        ]:
            abort(403)

        if request.method == 'OPTIONS':
            # pre-flight request, check CORS headers directly
            resp: BaseResponse = app.make_default_options_response()
        else:
            resp = make_response(f(*args, **kwargs))
        return add_headers(resp, origin)

    return wrapper


def csv_response(
    headers: list[str],
    rows: Sequence[Any],
    row_type: Literal['dict'] | None = None,
    row_handler: Callable[[list[Any]], list[Any] | dict[str, Any]] | None = None,
) -> Response:
    """
    Return a CSV response given a list of headers and rows of data.

    The default type of row is a list or a tuple of values. If row is of type dict set
    the `row_type` parameter to 'dict'.

    Accepts an optional row_handler function that can be used to transform the row.
    """
    csv_writer: Any
    stream = StringIO()
    if row_type == 'dict':
        csv_writer = csv.DictWriter(
            stream, fieldnames=headers, extrasaction='ignore', quoting=csv.QUOTE_MINIMAL
        )
        csv_writer.writeheader()
    else:
        csv_writer = csv.writer(stream, quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(headers)
    if callable(row_handler):
        csv_writer.writerows(row_handler(row) for row in rows)
    else:
        csv_writer.writerows(rows)
    return Response(stream.getvalue(), mimetype='text/csv')


def api_error(
    message: str, status_code: int = 400, errors: Sequence[str] = ()
) -> Response:
    """
    Generate a HTTP response as a JSON object for a failure scenario.

    :param message: Human readable error message to be included as part of the JSON
        response
    :param errors: Error messages to be included as part of the JSON response
    :param status_code: HTTP status code to be used for the response
    """
    return make_response(
        {'status': 'error', 'errors': errors, 'message': message}, status_code
    )


def api_success(result: Any, doc: str, status_code: int = 200) -> Response:
    """
    Generate a HTTP response as a JSON object for a success scenario.

    :param result: Top-level data to be encoded as JSON
    :param doc: Documentation to be included as part of the JSON response
    :param status_code: HTTP status code to be used for the response
    """
    return make_response({'status': 'ok', 'doc': doc, 'result': result}, status_code)
