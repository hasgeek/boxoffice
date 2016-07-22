# -*- coding: utf-8 -*-

from .. import app
from flask import jsonify, make_response
from utils import cors


class APIError(Exception):

    def __init__(self, message, status_code, response_message):
        super(APIError, self).__init__()
        self.message = message
        self.status_code = status_code
        self.response_message = response_message


@app.errorhandler(APIError)
@cors
def handle_api_error(error):
    app.logger.warning('Boxoffice API Error: {error}'.format(error=error.message))
    return make_response(jsonify(message=error.response_message), error.status_code)
