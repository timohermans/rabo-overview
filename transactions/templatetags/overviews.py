from typing import Any, Dict, List, Optional

from django import template
from transactions.models import Transaction

register = template.Library()


@register.inclusion_tag("transactions/components/transactions_box.html")
def show_transactions_box(
    transactions: List[Transaction], title: str, sub_title: Optional[str]
) -> Dict[str, Any]:
    return {"title": title, "sub_title": sub_title, "transactions": transactions}
