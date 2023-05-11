from baseframe import __, forms

__all__ = ['PriceForm']


class PriceForm(forms.Form):
    amount = forms.DecimalField(
        __("Amount"),
        validators=[
            forms.validators.InputRequired(__("Please specify an price amount")),
            forms.validators.NumberRange(min=0),
        ],
    )
    currency = forms.SelectField(
        __("Currency"), choices=[('INR', 'INR')], default='INR'
    )
    start_at = forms.DateTimeField(
        __("Start date & time"),
        validators=[
            forms.validators.DataRequired(__("Please specify a start date & time"))
        ],
        naive=False,
    )
    end_at = forms.DateTimeField(
        __("End date & time"),
        validators=[
            forms.validators.DataRequired(__("Please specify an end date & time")),
            forms.validators.GreaterThan(
                'start_at', __("The price can’t end before it starts")
            ),
        ],
        naive=False,
    )
