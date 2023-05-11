from baseframe import __
from coaster.utils import LabeledEnum

__all__ = ['RAZORPAY_PAYMENT_STATUS']


class RAZORPAY_PAYMENT_STATUS(LabeledEnum):  # noqa: N801
    """
    Reflects payment statuses.

    The list of states is as specifid in Razorpay documentation at
    https://razorpay.com/docs/payment-gateway/payments/#payment-life-cycle

    The values are ours. Razorpay sends back string values.
    """

    CREATED = (0, __("Created"))
    AUTHORIZED = (1, __("Authorized"))
    CAPTURED = (2, __("Captured"))
    #: Only fully refunded payments.
    REFUNDED = (3, __("Refunded"))
    FAILED = (4, __("Failed"))
