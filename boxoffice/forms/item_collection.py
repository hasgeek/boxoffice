# -*- coding: utf-8 -*-

from pycountry import pycountry
from baseframe import __
import baseframe.forms as forms
from boxoffice.data import indian_states

__all__ = ['ItemCollectionForm']


class ItemCollectionForm(forms.Form):
    title = forms.StringField(__("Item Collection title"),
        validators=[forms.validators.DataRequired(__("Please specify a title")),
        forms.validators.Length(max=250)], filters=[forms.filters.strip()])
    description_html = forms.TinyMce4Field(__("Description"))
    tax_type = forms.SelectField(__("Tax type"), choices=[('GST', 'GST')], default='GST')
    place_supply_state_code = forms.SelectField(__("State"),
        choices=[(state['short_code'], state['name']) for state in sorted(indian_states, key=lambda k: k['name'])],
        description=__("Place of supply"),
        default='KA')
    place_supply_country_code = forms.SelectField(__("Country"),
        choices=[(country.alpha_2, country.name) for country in sorted(pycountry.countries, key=lambda k: k.name)],
        description=__("Place of supply"),
        default='IN')
