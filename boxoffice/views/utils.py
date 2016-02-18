from flask import request, abort
from functools import wraps


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
