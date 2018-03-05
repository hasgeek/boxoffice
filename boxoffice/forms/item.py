# -*- coding: utf-8 -*-

from baseframe import __
import baseframe.forms as forms
from baseframe.forms.sqlalchemy import QuerySelectField
from ..models import db, Category, ItemCollection

__all__ = ['ItemForm']


class ItemForm(forms.Form):
    title = forms.StringField(__("Item title"),
        validators=[forms.validators.DataRequired(__("Please specify a title")),
            forms.validators.Length(max=250)], filters=[forms.filters.strip()])
    description_html = forms.TinyMce4Field(__("Description"),
        validators=[forms.validators.DataRequired(__("Please specify a description"))])
    seq = forms.IntegerField(__("Sequence"),
        description=__("The sequence of the ticket on the listing"),
        validators=[forms.validators.DataRequired(__("Please specify the sequence order"))])
    category = QuerySelectField(__("Category"), get_label='title',
        validators=[forms.validators.DataRequired(__("Please select a category"))])
    quantity_total = forms.IntegerField(__("Quantity available"),
        validators=[forms.validators.DataRequired(__("Please specify the quantity available for sale"))])
    assignee_details_html = forms.TextAreaField(__("Assignee details"))
    cancellable_until = forms.DateTimeField(__("Cancellable until"), validators=[forms.validators.Optional()])

    def set_queries(self):
        self.category.query = Category.query.join(ItemCollection).filter(
            Category.item_collection == self.edit_parent).options(db.load_only('id', 'title'))
