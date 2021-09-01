from apps.transactions.models import Account
from datetime import date
from typing import Any, Dict, List

from dateutil.relativedelta import relativedelta
from django import template
from django.db.models.base import Model
from django.forms.models import model_to_dict

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

@register.filter
def filter_receivers(accounts: List[Account]) -> List[Account]:
    return [a for a in accounts if a.is_user_owner == True]