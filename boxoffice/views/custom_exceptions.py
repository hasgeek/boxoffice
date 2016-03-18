from flask import jsonify
from .. import app


class APIError(Exception):

    def __init__(self, message, status_code):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code


@app.errorhandler(APIError)
def handle_api_error(error):
    return jsonify(message=error.message), error.status_code
