# validators.py

import re
from rest_framework.exceptions import ValidationError

PATTERN_USERNAME = re.compile(r'^[\w.@+-]+\Z')
PATTERN_EMAIL = re.compile('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+.[a-zA-Z0-9-.]+$')


def validate_username(value):
    if not PATTERN_USERNAME.match(value):
        raise ValidationError('Invalid username format.')
    return value


def validate_email(value):
    if not PATTERN_EMAIL.match(value):
        raise ValidationError('Invalid email format.')
    return value
