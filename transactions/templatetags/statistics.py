from transactions.models import Transaction
from django import template
from typing import List

register = template.Library()

@register.filter
def top_expenses(transactions: List[Transaction]) -> List[Transaction]:
	pass