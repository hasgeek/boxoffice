"""All enums."""

from __future__ import annotations

from baseframe import __
from coaster.utils import LabeledEnum

__all__ = [
    'DISCOUNT_TYPE',
    'INVOICE_STATUS',
    'GST_TYPE',
    'LINE_ITEM_STATUS',
    'ORDER_STATUS',
    'TRANSACTION_METHOD',
    'TRANSACTION_TYPE',
    'CURRENCY',
    'CURRENCY_SYMBOL',
    'RAZORPAY_PAYMENT_STATUS',
]


class DISCOUNT_TYPE(LabeledEnum):  # noqa: N801
    AUTOMATIC = (0, __("Automatic"))
    COUPON = (1, __("Coupon"))


class INVOICE_STATUS(LabeledEnum):  # noqa: N801
    DRAFT = (0, __("Draft"))
    FINAL = (1, __("Final"))


class GST_TYPE(LabeledEnum):  # noqa: N801
    GOOD = (0, __("Good"))
    SERVICE = (1, __("Service"))


class LINE_ITEM_STATUS(LabeledEnum):  # noqa: N801
    CONFIRMED = (0, __("Confirmed"))
    CANCELLED = (1, __("Cancelled"))
    PURCHASE_ORDER = (2, __("Purchase Order"))
    # A line item can be made void by the system to invalidate it. Eg: a discount no
    # longer applicable on a line item as a result of a cancellation
    VOID = (3, __("Void"))
    TRANSACTION = {CONFIRMED, VOID, CANCELLED}


class ORDER_STATUS(LabeledEnum):  # noqa: N801
    PURCHASE_ORDER = (0, __("Purchase Order"))
    SALES_ORDER = (1, __("Sales Order"))
    INVOICE = (2, __("Invoice"))
    CANCELLED = (3, __("Cancelled Order"))

    CONFIRMED = {SALES_ORDER, INVOICE}
    TRANSACTION = {SALES_ORDER, INVOICE, CANCELLED}


class TRANSACTION_METHOD(LabeledEnum):  # noqa: N801
    ONLINE = (0, __("Online"))
    CASH = (1, __("Cash"))
    BANK_TRANSFER = (2, __("Bank Transfer"))


class TRANSACTION_TYPE(LabeledEnum):  # noqa: N801
    PAYMENT = (0, __("Payment"))
    REFUND = (1, __("Refund"))
    # CREDIT = (2, __("Credit"))


class CURRENCY(LabeledEnum):
    INR = ("INR", __("INR"))


class CURRENCY_SYMBOL(LabeledEnum):  # noqa: N801
    INR = ('INR', '₹')


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
    FAILED = (4, __("Failed"))
    FAILED = (4, __("Failed"))
