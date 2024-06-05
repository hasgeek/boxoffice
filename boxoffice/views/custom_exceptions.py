from flask import Response, make_response

from .. import app


class PaymentGatewayError(Exception):
    def __init__(self, message: str, status_code: int, response_message: str) -> None:
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.response_message = response_message


@app.errorhandler(PaymentGatewayError)
def handle_api_error(error: PaymentGatewayError) -> Response:
    app.logger.error("Boxoffice Payment Gateway Error: %s", error.message)
    return make_response(
        {
            'status': 'error',
            'error': 'payment_gateway_error',
            'error_description': error.response_message,
        },
        error.status_code,
    )
