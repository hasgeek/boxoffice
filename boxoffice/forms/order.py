# -*- coding: utf-8 -*-

from baseframe import __
import baseframe.forms as forms
from boxoffice.data import indian_states_dict

__all__ = ['LineItemForm', 'BuyerForm', 'OrderSessionForm', 'RefundTransactionForm', 'InvoiceForm']


def trim(length):
    """
    Returns data trimmed to the given length. To be used as part of the filters argument.
    Eg:
    field = forms.StringField(__("Some field"), filters=[trim(25)])
    """
    def _inner(data):
        return unicode(data[0:length])
    return _inner


class LineItemForm(forms.Form):
    quantity = forms.IntegerField(__("Quantity"), validators=[forms.validators.DataRequired()])
    item_id = forms.StringField(__("Item Id"), validators=[forms.validators.DataRequired()])

    @classmethod
    def process_list(cls, line_items_json):
        """
        Returns a list of LineItemForm objects,
        returns an empty array if validation fails on any object
        """
        line_item_forms = []

        for line_item_dict in line_items_json:
            # Since some requests are cross-domain, other checks
            # have been introduced to ensure against CSRF, such as
            # a white-list of allowed origins and XHR only requests
            line_item_form = cls.from_json(line_item_dict, meta={'csrf': False})
            if not line_item_form.validate():
                return []
            line_item_forms.append(line_item_form)
        return line_item_forms


class BuyerForm(forms.Form):
    email = forms.EmailField(__("Email"), validators=[forms.validators.DataRequired(), forms.validators.Length(max=80)])
    fullname = forms.StringField(__("Full name"), validators=[forms.validators.DataRequired(), forms.validators.Length(max=80)])
    phone = forms.StringField(__("Phone number"), validators=[forms.validators.Length(max=16)])


class OrderSessionForm(forms.Form):
    utm_campaign = forms.StringField(__("UTM Campaign"), filters=[trim(250)])
    utm_source = forms.StringField(__("UTM Source"), filters=[trim(250)])
    utm_medium = forms.StringField(__("UTM Medium"), filters=[trim(250)])
    utm_term = forms.StringField(__("UTM Term"), filters=[trim(250)])
    utm_content = forms.StringField(__("UTM Content"), filters=[trim(250)])
    utm_id = forms.StringField(__("UTM Id"), filters=[trim(250)])
    gclid = forms.StringField(__("Gclid"), filters=[trim(250)])
    referrer = forms.StringField(__("Referrer"), filters=[trim(2083)])


class RefundTransactionForm(forms.Form):
    amount = forms.IntegerField(__("Amount"),
        validators=[forms.validators.DataRequired(__("Please specify an amount"))])
    internal_note = forms.StringField(__("Internal note"),
        validators=[forms.validators.Length(max=250)],
        description=__("Add a note for future reference"), filters=[forms.filters.none_if_empty()])
    refund_description = forms.StringField(__("Refund description"),
        validators=[forms.validators.Length(max=250)],
        description=__("Why is this order receiving a refund?"), filters=[forms.filters.none_if_empty()])
    note_to_user = forms.MarkdownField(__("Note to user"),
        description=__("Send this note to the buyer"), filters=[forms.filters.none_if_empty()])


def validate_state_code(form, field):
    # Note: state_code is only a required field if the chosen country is India
    if form.country_code.data == "IN":
        if field.data.upper() not in indian_states_dict:
            raise forms.validators.StopValidation(__("Please select a state"))


class InvoiceForm(forms.Form):
    buyer_taxid = forms.StringField(__("GSTIN"), validators=[forms.validators.Optional(),
        forms.validators.Length(max=255)], filters=[forms.filters.strip(), forms.filters.none_if_empty()])
    invoicee_name = forms.StringField(__("Full name"), validators=[forms.validators.DataRequired(__("Please enter the buyer's fullname")),
        forms.validators.Length(max=255)], filters=[forms.filters.strip()])
    invoicee_email = forms.EmailField(__("Email"), validators=[forms.validators.DataRequired(__("Please enter an email address")),
        forms.validators.Length(min=5, max=80),
        forms.validators.ValidEmail(__("Please enter a valid email"))],
        filters=[forms.filters.strip()])
    street_address_1 = forms.StringField(__("Street address 1"), validators=[forms.validators.DataRequired(__("Please enter the street address")),
        forms.validators.Length(max=255)], filters=[forms.filters.strip()])
    street_address_2 = forms.StringField(__("Street address 2"), validators=[forms.validators.Optional(),
        forms.validators.Length(max=255)], filters=[forms.filters.strip()])
    city = forms.StringField(__("City"), validators=[forms.validators.DataRequired(__("Please enter the city")),
        forms.validators.Length(max=255)], filters=[forms.filters.strip()])
    country_code = forms.StringField(__("Country"), validators=[forms.validators.DataRequired(__("Please select a country")),
        forms.validators.Length(max=2)], filters=[forms.filters.strip()])
    state_code = forms.StringField(__("State code"), validators=[forms.validators.Length(max=4),
        validate_state_code], filters=[forms.filters.strip()])
    state = forms.StringField(__("State"), validators=[forms.validators.Optional(),
        forms.validators.Length(max=255)], filters=[forms.filters.strip(), forms.filters.none_if_empty()])
    postcode = forms.StringField(__("Postcode"), validators=[forms.validators.DataRequired(__("Please enter a postcode")),
        forms.validators.Length(max=8)], filters=[forms.filters.strip()])
