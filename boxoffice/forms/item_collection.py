from __future__ import annotations

from baseframe import __, forms, localized_country_list

from ..data import indian_states, indian_states_dict

__all__ = ['ItemCollectionForm']


class ItemCollectionForm(forms.Form):
    title = forms.StringField(
        __("Item Collection title"),
        validators=[
            forms.validators.DataRequired(__("Please specify a title")),
            forms.validators.Length(max=250),
        ],
        filters=[forms.filters.strip()],
    )
    description_html = forms.TinyMce4Field(
        __("Description"),
        validators=[forms.validators.DataRequired(__("Please specify a description"))],
    )
    tax_type = forms.SelectField(
        __("Tax type"), choices=[('GST', 'GST')], default='GST'
    )
    place_supply_state_code = forms.SelectField(
        __("State"),
        description=__("State of supply"),
        coerce=int,
        default=indian_states_dict['KA']['short_code'],
        validators=[forms.validators.DataRequired(__("Please select a state"))],
    )
    place_supply_country_code = forms.SelectField(
        __("Country"),
        description=__("Country of supply"),
        default='IN',
        validators=[forms.validators.DataRequired(__("Please select a country"))],
    )

    def set_queries(self) -> None:
        self.place_supply_state_code.choices = [(0, '')] + [
            (state['short_code'], state['name'])
            for state in sorted(indian_states, key=lambda k: k['name'])
        ]
        self.place_supply_country_code.choices = [('', '')] + localized_country_list()

    def validate_place_supply_state_code(self, field: forms.Field) -> None:
        if field.data <= 0:
            # state short codes start from 1,
            # and 0 means empty value as mentioned above in set_queries
            raise forms.ValidationError(__("Please select a state"))
