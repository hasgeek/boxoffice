# -*- coding: utf-8 -*-

from baseframe import __
import baseframe.forms as forms
from baseframe.forms import ValidationError


__all__ = ['LineItemForm', 'BuyerForm', 'OrderSessionForm']


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
            line_item_form = cls.from_json(line_item_dict)
            # Since some requests are cross-domain, other checks
            # have been introduced to ensure against CSRF, such as
            # a white-list of allowed origins and XHR only requests
            line_item_form.csrf_enabled = False
            if not line_item_form.validate():
                return []
            line_item_forms.append(line_item_form)
        return line_item_forms


class BuyerForm(forms.Form):
    email = forms.EmailField(__("Email"), validators=[forms.validators.DataRequired(), forms.validators.Length(max=80)])
    fullname = forms.StringField(__("Full name"), validators=[forms.validators.DataRequired()])
    phone = forms.StringField(__("Phone number"), validators=[forms.validators.Length(max=16)])


class OrderSessionForm(forms.Form):
    utm_campaign = forms.StringField(__("UTM Campaign"), validators=[forms.validators.DataRequired(), forms.validators.Length(max=250)])
    utm_source = forms.StringField(__("UTM Source"), validators=[forms.validators.Length(max=250)])
    utm_medium = forms.StringField(__("UTM Medium"), validators=[forms.validators.Length(max=250)])
    utm_term = forms.StringField(__("UTM Term"), validators=[forms.validators.Length(max=250)])
    utm_content = forms.StringField(__("UTM Content"), validators=[forms.validators.Length(max=250)])
    utm_id = forms.StringField(__("UTM Id"), validators=[forms.validators.Length(max=250)])
    gclid = forms.StringField(__("Gclid"), validators=[forms.validators.Length(max=250)])
    referrer = forms.StringField(__("Referrer"), validators=[forms.validators.Length(max=2083)])
