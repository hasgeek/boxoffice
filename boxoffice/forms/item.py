# -*- coding: utf-8 -*-

import json
from baseframe import __
import baseframe.forms as forms
from baseframe.forms.sqlalchemy import QuerySelectField
from ..models import db, Category, ItemCollection

__all__ = ['ItemForm']


class JSONField(forms.TextAreaField):
    def _value(self):
        if self.raw_data:
            return self.raw_data[0]
        elif self.data:
            # prevent utf8 characters from being converted to ascii
            return unicode(json.dumps(self.data, ensure_ascii=False))
        else:
            return ''

    def process_formdata(self, valuelist):
        if valuelist:
            value = valuelist[0]

            # allow saving blank field as None
            if not value:
                self.data = None
                return

            try:
                self.data = json.loads(valuelist[0])
            except ValueError:
                raise ValueError(self.gettext('Invalid JSON'))


class ItemForm(forms.Form):
    title = forms.StringField(__("Item title"),
        validators=[forms.validators.DataRequired(__("Please specify a title")),
            forms.validators.Length(max=250)], filters=[forms.filters.strip()])
    description = forms.TinyMce4Field(__("Description"),
        validators=[forms.validators.DataRequired(__("Please specify a description"))])
    seq = forms.IntegerField(__("Sequence"),
        description=__("The sequence of the ticket on the listing"),
        validators=[forms.validators.DataRequired(__("Please specify the sequence order"))])
    category = QuerySelectField(__("Category"), get_label='title',
        validators=[forms.validators.DataRequired(__("Please select a category"))])
    quantity_total = forms.IntegerField(__("Quantity available"),
        validators=[forms.validators.DataRequired(__("Please specify the quantity available for sale"))])
    assignee_details = JSONField(__("Assignee details"))
    cancellable_until = forms.DateTimeField(__("Cancellable until"), validators=[forms.validators.Optional()])

    def set_queries(self):
        self.category.query = Category.query.join(ItemCollection).filter(
            Category.item_collection == self.edit_parent).options(db.load_only('id', 'title'))
