from baseframe import __
import baseframe.forms as forms


__all__ = ['LineItemForm', 'BuyerForm']


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
            if not line_item_form.validate():
                return []
            line_item_forms.append(line_item_form)
        return line_item_forms


class BuyerForm(forms.Form):
    email = forms.EmailField(__("Email"), validators=[forms.validators.DataRequired(), forms.validators.Length(max=80)])
    fullname = forms.StringField(__("Full Name"), validators=[forms.validators.DataRequired()])
    phone = forms.StringField(__("Phone number"), validators=[forms.validators.Length(max=13)])
