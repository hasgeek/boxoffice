# -*- coding: utf-8 -*-

import json
from flask import request
from html5print import HTMLBeautifier
from pycountry import pycountry
from baseframe import __
import baseframe.forms as forms
from baseframe.forms.sqlalchemy import QuerySelectField
from ..models import db, Category, ItemCollection
from boxoffice.data import indian_states, indian_states_dict

__all__ = ['ItemForm']


def format_json(data):
    if request.method == 'GET':
        return json.dumps(data, indent=4, sort_keys=True)
    # `json.loads` doesn't raise an exception for "null"
    # so assign a default value of `{}`
    if not data or data == 'null':
        return json.dumps({})
    return data


def format_description(data):
    if request.method == 'GET' and data:
        return HTMLBeautifier.beautify(data.text, 8)
    return data


ASSIGNEE_DETAILS_PLACEHOLDER = {
    "childcare": {
        "label": "Do you need childcare?",
        "field_type": "checkbox",
        "option": "yes"
    },
    "city": {
        "label": "City",
        "field_type": "string"
    },
    "food_options": {
        "label": "Food preference",
        "field_type": "select",
        "options": ["Veg", "Non-veg"]
    },
    "survey": {
        "label": "How did you hear about this event?",
        "field_type": "textbox",
    }
}


def validate_json(form, field):
    try:
        json.loads(field.data)
    except ValueError:
        raise forms.validators.StopValidation(__("Invalid JSON"))


class ItemForm(forms.Form):
    title = forms.StringField(__("Item title"),
        validators=[forms.validators.DataRequired(__("Please specify a title")),
            forms.validators.Length(max=250)], filters=[forms.filters.strip()])
    description = forms.TextAreaField(__("Description"), filters=[format_description],
        validators=[forms.validators.DataRequired(__("Please specify a description"))])
    restricted_entry = forms.BooleanField(__("Restrict entry?"))
    seq = forms.IntegerField(__("Sequence"),
        description=__("The sequence of the ticket on the listing"),
        validators=[forms.validators.DataRequired(__("Please specify the sequence order"))])
    category = QuerySelectField(__("Category"), get_label='title',
        validators=[forms.validators.DataRequired(__("Please select a category"))])
    quantity_total = forms.IntegerField(__("Quantity available"),
        validators=[forms.validators.DataRequired(__("Please specify the quantity available for sale"))])
    assignee_details = forms.TextAreaField(__("Assignee details"), filters=[format_json],
        validators=[validate_json], default=ASSIGNEE_DETAILS_PLACEHOLDER)
    event_date = forms.DateField(__("Event date"), validators=[forms.validators.DataRequired(__("Please specify a date for the event"))])
    cancellable_until = forms.DateTimeField(__("Cancellable until"), validators=[forms.validators.Optional()])
    place_supply_state_code = forms.SelectField(__("State"),
        choices=[(state['short_code'], state['name']) for state in sorted(indian_states, key=lambda k: k['name'])],
        description=__("Place of supply"), coerce=int,
        default=indian_states_dict['KA']['short_code'])
    place_supply_country_code = forms.SelectField(__("Country"),
        choices=[(country.alpha_2, country.name) for country in sorted(pycountry.countries, key=lambda k: k.name)],
        description=__("Place of supply"),
        default='')

    def set_queries(self):
        self.category.query = Category.query.join(ItemCollection).filter(
            Category.item_collection == self.edit_parent).options(db.load_only('id', 'title'))
