from typing import Any, Dict

from django import template

from apps.transactions.utils.summary import Summary

register = template.Library()


@register.inclusion_tag("transactions/components/receiver_overviews.html")
def receiver_overviews(**kwargs: dict) -> Dict[str, Any]:
    """Overviews of the different accounts you own"""
    return {"receivers": kwargs.pop("receivers"), "transactions": kwargs.pop("transactions")}


@register.inclusion_tag("transactions/components/summary_text.html")
def summary_text(summary: Summary) -> Dict[str, Any]:
    """Text version of what you did in the period you uploaded"""
    return {"summary": summary}
