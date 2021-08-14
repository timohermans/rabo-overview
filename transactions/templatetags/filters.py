from datetime import date

from dateutil.relativedelta import relativedelta
from django import template

register = template.Library()


@register.filter
def previous_month(source: date) -> date:
    return date(source.year, source.month, 1) - relativedelta(months=1)


@register.filter
def next_month(source: date) -> date:
    return date(source.year, source.month, 1) + relativedelta(months=1)


@register.filter
def to_date_string(source: date) -> str:
    return source.isoformat()
