# -*- coding: utf-8 -*-

import json
from flask import request
import baseframe.forms as forms
from baseframe import __


def validate_json(form, field):
    try:
        json.loads(field.data)
    except ValueError:
        raise forms.validators.StopValidation(__("Invalid JSON"))


def format_json(data):
    if request.method == 'GET':
        return json.dumps(data, indent=4, sort_keys=True)
    # `json.loads` doesn't raise an exception for "null"
    # so assign a default value of `{}`
    if not data or data == 'null':
        return json.dumps({})
    return data
