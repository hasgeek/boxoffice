from __future__ import annotations

from baseframe import __, forms, localized_country_list

from ..data import indian_states, indian_states_dict
from ..models import Category, ItemCollection, sa

__all__ = ['ItemForm']


ASSIGNEE_DETAILS_PLACEHOLDER = {
    "childcare": {
        "label": "Do you need childcare?",
        "field_type": "checkbox",
        "option": "yes",
    },
    "city": {"label": "City", "field_type": "string"},
    "food_options": {
        "label": "Food preference",
        "field_type": "select",
        "options": ["Veg", "Non-veg"],
    },
    "survey": {
        "label": "How did you hear about this event?",
        "field_type": "textbox",
    },
}


class ItemForm(forms.Form):
    title = forms.StringField(
        __("Item title"),
        validators=[
            forms.validators.DataRequired(__("Please specify a title")),
            forms.validators.Length(max=250),
        ],
        filters=[forms.filters.strip()],
    )
    description = forms.TextAreaField(
        __("Description"),
        validators=[forms.validators.DataRequired(__("Please specify a description"))],
    )
    restricted_entry = forms.BooleanField(__("Restrict entry?"))
    seq = forms.IntegerField(
        __("Sequence"),
        description=__("The sequence of the ticket on the listing"),
        validators=[
            forms.validators.DataRequired(__("Please specify the sequence order"))
        ],
    )
    category = forms.QuerySelectField(
        __("Category"),
        get_label='title',
        validators=[forms.validators.DataRequired(__("Please select a category"))],
    )
    quantity_total = forms.IntegerField(
        __("Quantity available"),
        validators=[
            forms.validators.DataRequired(
                __("Please specify the quantity available for sale")
            )
        ],
    )
    assignee_details = forms.JsonField(
        __("Assignee details"), default=ASSIGNEE_DETAILS_PLACEHOLDER
    )
    event_date = forms.DateField(
        __("Event date"),
        description=__("The date on which this item will be invoiced"),
        validators=[
            forms.validators.DataRequired(__("Please specify a date for the event"))
        ],
    )
    transferable_until = forms.DateTimeField(
        __("Transferable until"), validators=[forms.validators.Optional()], naive=False
    )
    cancellable_until = forms.DateTimeField(
        __("Cancellable until"), validators=[forms.validators.Optional()], naive=False
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
        self.category.query = (
            Category.query.join(ItemCollection)
            .filter(Category.item_collection == self.edit_parent)
            .options(sa.orm.load_only(Category.id, Category.title))
        )

    def validate_place_supply_state_code(self, field: forms.Field) -> None:
        if field.data <= 0:
            # state short codes start from 1,
            # and 0 means empty value as mentioned above in set_queries
            raise forms.ValidationError(__("Please select a state"))

    def validate_transferable_until(self, field: forms.Field) -> None:
        if field.data and field.data.date() > self.event_date.data:
            raise forms.ValidationError(
                __("Ticket transfer deadline cannot be after event date")
            )
