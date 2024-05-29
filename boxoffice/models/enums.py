"""All enums."""

from __future__ import annotations

from enum import IntEnum, StrEnum
from typing import Final

from baseframe import __

__all__ = [
    'DiscountTypeEnum',
    'InvoiceStatus',
    'LineItemStatus',
    'OrderStatus',
    'TransactionMethodEnum',
    'TransactionTypeEnum',
    'CurrencyEnum',
    'CurrencySymbol',
    'RazorpayPaymentStatus',
]


class DiscountTypeEnum(IntEnum):
    AUTOMATIC = 1
    COUPON = 2

    __titles__: Final = {AUTOMATIC: __("Automatic"), COUPON: __("Coupon")}

    def __init__(self, value: int) -> None:
        self.title = self.__titles__[value]  # pylint: disable=unsubscriptable-object


class InvoiceStatus(IntEnum):
    DRAFT = 1
    FINAL = 2


class LineItemStatus(IntEnum):
    CONFIRMED = 1
    CANCELLED = 2
    PURCHASE_ORDER = 3
    # A line item can be made void by the system to invalidate it. Eg: a discount no
    # longer applicable on a line item as a result of a cancellation
    VOID = 4


class OrderStatus(IntEnum):
    PURCHASE_ORDER = 1
    SALES_ORDER = 2
    INVOICE = 3
    CANCELLED = 4


class TransactionMethodEnum(IntEnum):
    ONLINE = 1
    CASH = 2
    BANK_TRANSFER = 3


class TransactionTypeEnum(IntEnum):
    PAYMENT = 1
    REFUND = 2


class CurrencyEnum(StrEnum):
    INR = "INR"


class CurrencySymbol(StrEnum):
    INR = '₹'


class RazorpayPaymentStatus(IntEnum):
    """
    Reflects payment statuses.

    The list of states is as specified in Razorpay documentation at
    https://razorpay.com/docs/payment-gateway/payments/#payment-life-cycle

    The values are ours. Razorpay sends back string values.
    """

    CREATED = 1
    AUTHORIZED = 2
    CAPTURED = 3
    REFUNDED = 4  # Only fully refunded payments
    FAILED = 5
