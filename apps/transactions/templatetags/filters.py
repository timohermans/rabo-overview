from datetime import date
from typing import Any, Iterator, List

from dateutil.relativedelta import relativedelta
from django import template

from apps.transactions.models import Account, Transaction

register = template.Library()


@register.filter
def previous_month(source: date) -> date:
    """date - 1"""
    return date(source.year, source.month, 1) - relativedelta(months=1)


@register.filter
def next_month(source: date) -> date:
    """date + 1"""
    return date(source.year, source.month, 1) + relativedelta(months=1)


@register.filter
def to_date_string(source: date) -> str:
    """date string for month hrefs"""
    return source.isoformat()


@register.filter
def receivers(accounts: List[Account]) -> List[Account]:
    """pulls out receivers from all accounts"""
    return [a for a in accounts if a.is_user_owner is True]


@register.filter
def short_account_number(account_number: str) -> str:
    """long IBANs are way too hard to read"""
    return f"{account_number[:2]}...{account_number[-4:]}"


@register.filter
def of_receiver(
    transactions: List[Transaction], receiver: Account
) -> Iterator[Transaction]:
    """returns transactions of a user owned account"""
    return (t for t in transactions if t.receiver == receiver)

@register.filter
def get(o: object, key: str) -> Any:
    """I want property access in templates!"""
    return getattr(o, key)
