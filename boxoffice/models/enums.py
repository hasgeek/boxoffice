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
    AUTOMATIC = 0
    COUPON = 1

    __titles__: Final = {AUTOMATIC: __("Automatic"), COUPON: __("Coupon")}

    def __init__(self, value: int) -> None:
        self.title = self.__titles__[value]


class InvoiceStatus(IntEnum):
    DRAFT = 0
    FINAL = 1


class LineItemStatus(IntEnum):
    CONFIRMED = 0
    CANCELLED = 1
    PURCHASE_ORDER = 2
    # A line item can be made void by the system to invalidate it. Eg: a discount no
    # longer applicable on a line item as a result of a cancellation
    VOID = 3


class OrderStatus(IntEnum):
    PURCHASE_ORDER = 0
    SALES_ORDER = 1
    INVOICE = 2
    CANCELLED = 3


class TransactionMethodEnum(IntEnum):
    ONLINE = 0
    CASH = 1
    BANK_TRANSFER = 2


class TransactionTypeEnum(IntEnum):
    PAYMENT = 0
    REFUND = 1


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

    CREATED = 0
    AUTHORIZED = 1
    CAPTURED = 2
    REFUNDED = 3  # Only fully refunded payments
    FAILED = 4
