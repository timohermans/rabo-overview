from typing import Any, Dict

from django import template

register = template.Library()


@register.inclusion_tag("transactions/components/receiver_overviews.html")
def receiver_overviews(**kwargs: dict) -> Dict[str, Any]:
    """Overviews of the different accounts you own"""
    return {"receivers": kwargs.pop("receivers"), "transactions": kwargs.pop("transactions")}
