from datetime import date

from dateutil.relativedelta import relativedelta
from django import template

register = template.Library()


@register.filter
def previous_month(source):
    if not isinstance(source, date):
        return date.today()

    return date(source.year, source.month, 1) - relativedelta(months=1)


@register.filter
def next_month(source):
    if not isinstance(source, date):
        return date.today()

    return date(source.year, source.month, 1) + relativedelta(months=1)


@register.filter
def to_date_string(source: date) -> str:
    print(source)
    return source.isoformat()


