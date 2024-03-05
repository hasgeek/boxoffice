from __future__ import annotations

from baseframe import _, __, forms
from baseframe.forms.validators import StopValidation

from ..models import Order

__all__ = ['OrderRefundForm']


class OrderRefundForm(forms.Form):
    edit_parent: Order

    amount = forms.IntegerField(
        __("Amount"),
        validators=[forms.validators.DataRequired(__("Please specify an amount"))],
    )
    internal_note = forms.StringField(
        __("Internal note"),
        validators=[
            forms.validators.DataRequired(
                __("Please specify a note for future reference")
            ),
            forms.validators.Length(max=250),
        ],
        description=__("Add a note for future reference"),
        filters=[forms.filters.none_if_empty()],
    )
    refund_description = forms.StringField(
        __("Refund description"),
        validators=[
            forms.validators.DataRequired(
                __("Please specify a description for the invoice")
            ),
            forms.validators.Length(max=250),
        ],
        description=__("Description for the invoice"),
        filters=[forms.filters.none_if_empty()],
    )
    note_to_user = forms.MarkdownField(
        __("Note to user"),
        validators=[
            forms.validators.DataRequired(__("Please specify a note for the buyer"))
        ],
        description=__("Send this note to the buyer"),
        filters=[forms.filters.none_if_empty()],
    )

    def validate_amount(self, field: forms.Field) -> None:
        requested_refund_amount = field.data
        order = self.edit_parent
        if not order.paid_amount:
            raise StopValidation(_("Refunds can only be issued for paid orders"))
        if (order.refunded_amount + requested_refund_amount) > order.paid_amount:
            raise StopValidation(
                _(
                    "Invalid refund amount! Must be lesser than {amount}, the net"
                    " amount paid for the order"
                ).format(amount=order.net_amount)
            )
