from transactions.models import Transaction
from django import template
from typing import List

register = template.Library()


@register.filter
def top_expenses(transactions: List[Transaction], limit: int) -> List[Transaction]:
    return [
        transaction
        for transaction in sorted(transactions, key=lambda t: t.amount)
        if transaction.other_party.is_user_owner == False
    ][:limit]


@register.filter
def top_incomes(transactions: List[Transaction], limit: int) -> List[Transaction]:
    return [
        transaction
        for transaction in sorted(transactions, key=lambda t: t.amount, reverse=True)
        if transaction.other_party.is_user_owner == False
    ][:limit]
