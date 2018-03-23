# -*- coding: utf-8 -*-

from baseframe import __
import baseframe.forms as forms
from baseframe.forms.validators import StopValidation
from boxoffice.models import Order

__all__ = ['OrderRefundForm']


def validate_amount(form, field):
    requested_refund_amount = field.data
    order = form.edit_parent
    if not order.paid_amount:
        raise StopValidation(__("Refunds can only be issued for paid orders"))
    if (order.refunded_amount + requested_refund_amount) > order.paid_amount:
        raise StopValidation(__("Invalid refund amount! Must be lesser than {amount}, the net amount paid for the order".format(amount=order.net_amount)))


class OrderRefundForm(forms.Form):
    amount = forms.IntegerField(__("Amount"),
        validators=[forms.validators.DataRequired(__("Please specify an amount")), validate_amount])
    internal_note = forms.StringField(__("Internal note"),
        validators=[forms.validators.Length(max=250)],
        description=__("Add a note for future reference"), filters=[forms.filters.none_if_empty()])
    refund_description = forms.StringField(__("Refund description"),
        validators=[forms.validators.Length(max=250)],
        description=__("Why is this order receiving a refund?"), filters=[forms.filters.none_if_empty()])
    note_to_user = forms.MarkdownField(__("Note to user"),
        description=__("Send this note to the buyer"), filters=[forms.filters.none_if_empty()])
