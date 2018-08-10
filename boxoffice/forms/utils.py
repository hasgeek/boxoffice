# -*- coding: utf-8 -*-

import json
import six
import baseframe.forms as forms
from baseframe import __


def validate_json(form, field):
    try:
        json.loads(field.data)
    except ValueError:
        raise forms.validators.StopValidation(__("Invalid JSON"))


def format_json(data):
    # `json.loads` doesn't raise an exception for "null"
    # so assign a default value of `{}`
    if not data or data == 'null':
        data = {}
    elif isinstance(data, six.string_types):
        # This happens when putting JSON data from the form into the database
        data = json.loads(data)
    return json.dumps(data, indent=4, sort_keys=True)
