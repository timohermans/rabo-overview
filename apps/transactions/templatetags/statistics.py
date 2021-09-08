from typing import List

from django import template

from apps.transactions.models import Account, Transaction
from apps.transactions.utils.summary import Summary

register = template.Library()


@register.filter
def top_expenses(transactions: List[Transaction], limit: int) -> List[Transaction]:
    """To get an idea what the biggest spenders were!"""
    return [
        transaction
        for transaction in sorted(transactions, key=lambda t: t.amount)
        if not transaction.other_party.is_user_owner
    ][:limit]


@register.filter
def top_incomes(transactions: List[Transaction], limit: int) -> List[Transaction]:
    """To get an idea where we get our money from"""
    return [
        transaction
        for transaction in sorted(transactions, key=lambda t: t.amount, reverse=True)
        if not transaction.other_party.is_user_owner
    ][:limit]


@register.filter
def summary(transactions: List[Transaction]) -> Summary:
    """Have a quick overview of what happened"""
    return Summary(transactions)
