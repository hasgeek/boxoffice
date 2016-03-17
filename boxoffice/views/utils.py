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


@app.template_filter('invoice_date')
def invoice_date_filter(date, format):
    return localize(date, app.config['TIMEZONE']).strftime(format)
