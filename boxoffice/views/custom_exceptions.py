from flask import jsonify, make_response

from .. import app
from .utils import cors


class PaymentGatewayError(Exception):
    def __init__(self, message, status_code, response_message):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.response_message = response_message


@app.errorhandler(PaymentGatewayError)
@cors
def handle_api_error(error):
    app.logger.warning('Boxoffice Payment Gateway Error: %s', error.message)
    return make_response(
        jsonify(
            {
                "status": "error",
                "error": "payment_gateway_error",
                "error_description": error.response_message,
            }
        ),
        error.status_code,
    )
