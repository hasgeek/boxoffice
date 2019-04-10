# -*- coding: utf-8 -*-

from baseframe import __, forms, localized_country_list
from boxoffice.data import indian_states, indian_states_dict

__all__ = ['ItemCollectionForm']


class ItemCollectionForm(forms.Form):
    title = forms.StringField(__("Item Collection title"),
        validators=[forms.validators.DataRequired(__("Please specify a title")),
        forms.validators.Length(max=250)], filters=[forms.filters.strip()])
    description_html = forms.TinyMce4Field(__("Description"),
        validators=[forms.validators.DataRequired(__("Please specify a description"))])
    tax_type = forms.SelectField(__("Tax type"), choices=[('GST', 'GST')], default='GST')
    place_supply_state_code = forms.SelectField(__("State"),
        choices=[('', '')] + [(state['short_code'], state['name']) for state in sorted(indian_states, key=lambda k: k['name'])],
        description=__("Place of supply"), coerce=int, default=indian_states_dict['KA']['short_code'],
        validators=[forms.validators.DataRequired(__("Please select a state"))])
    place_supply_country_code = forms.SelectField(__("Country"),
        choices=[('', '')],
        description=__("Place of supply"), default='IN',
        validators=[forms.validators.DataRequired(__("Please select a country"))])

    def set_queries(self):
        self.place_supply_country_code.choices += localized_country_list()
