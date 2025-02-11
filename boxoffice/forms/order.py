from __future__ import annotations

from collections.abc import Callable
from typing import Any, Self

from werkzeug.datastructures import ImmutableMultiDict

from baseframe import __, forms

from ..data import codes as gst_codes, indian_states_dict

__all__ = ['BuyerForm', 'InvoiceForm', 'LineItemForm', 'OrderSessionForm']


def trim(length: int) -> Callable[[str | None], str]:
    """
    Return data trimmed to the given length.

    To be used as part of the filters argument. Eg::

        field = forms.StringField(__("Some field"), filters=[trim(25)])
    """

    def _inner(data: str | None) -> str:
        return str((data or '')[0:length])

    return _inner


class LineItemForm(forms.Form):
    quantity = forms.IntegerField(
        __("Quantity"), validators=[forms.validators.DataRequired()]
    )
    ticket_id = forms.StringField(
        __("Item Id"), validators=[forms.validators.DataRequired()]
    )

    @classmethod
    def process_list(cls, line_items_json: list[Any]) -> list[Self]:
        """
        Return a list of LineItemForm objects.

        Returns an empty array if validation fails on any object.
        """
        line_item_forms = []

        for line_item_dict in line_items_json:
            # Since some requests are cross-domain, other checks
            # have been introduced to ensure against CSRF, such as
            # a white-list of allowed origins and XHR only requests
            line_item_form = cls(
                formdata=ImmutableMultiDict(line_item_dict), meta={'csrf': False}
            )
            if not line_item_form.validate():
                return []
            line_item_forms.append(line_item_form)
        return line_item_forms


class BuyerForm(forms.Form):
    email = forms.EmailField(
        __("Email"),
        validators=[
            forms.validators.DataRequired(__("Please enter an email address")),
            forms.validators.Length(min=5, max=80),
        ],
    )
    fullname = forms.StringField(
        __("Full name"),
        validators=[
            forms.validators.DataRequired(__("Please enter the buyer's full name")),
            forms.validators.Length(max=80),
        ],
    )
    phone = forms.StringField(
        __("Phone number"),
        validators=[
            forms.validators.DataRequired(__("Please enter a phone number")),
            forms.validators.Length(max=16),
        ],
    )


class OrderSessionForm(forms.Form):
    utm_campaign = forms.StringField(__("UTM Campaign"), filters=[trim(250)])
    utm_source = forms.StringField(__("UTM Source"), filters=[trim(250)])
    utm_medium = forms.StringField(__("UTM Medium"), filters=[trim(250)])
    utm_term = forms.StringField(__("UTM Term"), filters=[trim(250)])
    utm_content = forms.StringField(__("UTM Content"), filters=[trim(250)])
    utm_id = forms.StringField(__("UTM Id"), filters=[trim(250)])
    gclid = forms.StringField(__("Google Click Id"), filters=[trim(250)])
    referrer = forms.StringField(__("Referrer"), filters=[trim(2083)])
    host = forms.StringField(__("Host"), filters=[trim(2083)])


def validate_state_code(form: InvoiceForm, field: forms.Field) -> None:
    # Note: state_code is only a required field if the chosen country is India
    if form.country_code.data == "IN" and field.data.upper() not in indian_states_dict:
        raise forms.validators.StopValidation(__("Please select a state"))


def validate_gstin(_form: forms.Form, field: forms.Field) -> None:
    """
    Raise a StopValidation exception if the supplied field's data is not a valid GSTIN.

    Checks if the data is:
    - 15 characters in length
    - First two characters form a valid short code for an Indian state
    - Contains a PAN (alphanumeric sub-string ranging from the 2nd to the 11th
      character)
    - Last character is an alphanumeric

    Reference: https://cleartax.in/s/know-your-gstin
    """
    # 15 length, first 2 digits, valid pan, checksum
    if (
        len(field.data) != 15
        or int(field.data[:2]) not in gst_codes
        or not field.data[2:12].isalnum()
        or not field.data[-1].isalnum()
    ):
        raise forms.validators.StopValidation(
            __("This does not appear to be a valid GSTIN")
        )


class InvoiceForm(forms.Form):
    buyer_taxid = forms.StringField(
        __("GSTIN"),
        validators=[
            forms.validators.Optional(),
            forms.validators.Length(max=255),
            validate_gstin,
        ],
        filters=[forms.filters.strip(), forms.filters.none_if_empty()],
    )
    invoicee_name = forms.StringField(
        __("Full name"),
        validators=[
            forms.validators.DataRequired(__("Please enter the buyer's full name")),
            forms.validators.Length(max=255),
        ],
        filters=[forms.filters.strip()],
    )
    invoicee_company = forms.StringField(
        __("Company"),
        validators=[forms.validators.Optional(), forms.validators.Length(max=255)],
        filters=[forms.filters.strip()],
    )
    invoicee_email = forms.EmailField(
        __("Email"),
        validators=[
            forms.validators.DataRequired(__("Please enter an email address")),
            forms.validators.Length(min=5, max=80),
            forms.validators.ValidEmail(__("Please enter a valid email")),
        ],
        filters=[forms.filters.strip()],
    )
    street_address_1 = forms.StringField(
        __("Street address 1"),
        validators=[
            forms.validators.DataRequired(__("Please enter the street address")),
            forms.validators.Length(max=255),
        ],
        filters=[forms.filters.strip()],
    )
    street_address_2 = forms.StringField(
        __("Street address 2"),
        validators=[forms.validators.Optional(), forms.validators.Length(max=255)],
        filters=[forms.filters.strip()],
    )
    city = forms.StringField(
        __("City"),
        validators=[
            forms.validators.DataRequired(__("Please enter the city")),
            forms.validators.Length(max=255),
        ],
        filters=[forms.filters.strip()],
    )
    country_code = forms.StringField(
        __("Country"),
        validators=[
            forms.validators.DataRequired(__("Please select a country")),
            forms.validators.Length(max=2),
        ],
        filters=[forms.filters.strip()],
    )
    state_code = forms.StringField(
        __("State code"),
        validators=[forms.validators.Length(max=4), validate_state_code],
        filters=[forms.filters.strip()],
    )
    state = forms.StringField(
        __("State"),
        validators=[forms.validators.Optional(), forms.validators.Length(max=255)],
        filters=[forms.filters.strip(), forms.filters.none_if_empty()],
    )
    postcode = forms.StringField(
        __("Postcode"),
        validators=[
            forms.validators.DataRequired(__("Please enter a postcode")),
            forms.validators.Length(max=8),
        ],
        filters=[forms.filters.strip()],
    )
