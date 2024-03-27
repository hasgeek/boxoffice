"""Miscellaneous utility functions."""

import re

# https://incometaxindia.gov.in/Forms/tps/1.Permanent%20Account%20Number%20(PAN).pdf
PAN_RE = re.compile(r'^[A-Z]{3}[ABCFLPT][A-Z]\d{4}[A-Z]$', flags=re.I)
