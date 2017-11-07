# -*- coding: utf-8 -*-

from baseframe import __
from coaster.utils import LabeledEnum

__all__ = ['RAZORPAY_PAYMENT_STATUS']

class RAZORPAY_PAYMENT_STATUS(LabeledEnum):
    """
    Reflects payment statuses as specified in
    https://docs.razorpay.com/docs/return-objects
    """
    CREATED = (0, __("Created"))
    AUTHORIZED = (1, __("Authorized"))
    CAPTURED = (2, __("Captured"))
    #: Only fully refunded payments.
    REFUNDED = (3, __("Refunded"))
    FAILED = (4, __("Failed"))
