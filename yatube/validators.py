from datetime import date

from django.core.exceptions import ValidationError


def validate_no_future_date(val):
    if val > date.today():
        raise ValidationError('Дата не может быть будущей!')
