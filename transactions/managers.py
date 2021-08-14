from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Dict, Any, TYPE_CHECKING

from accounts.models import User as UserType
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q, Sum
from django.db.models.query import QuerySet

from transactions.utils.date import get_start_end_date_from

if TYPE_CHECKING:
    from accounts.models import User as UserType

User = get_user_model()


class ParseResult(Enum):
    SUCCESS = 1
    DUPLICATE = 2
    ERROR = 3

class StatisticsManager(models.Manager[Any]):
    def get_user_queryset(self, user: UserType) -> QuerySet[Any]:
        return super().get_queryset().filter(user=user)

    def get_queryset_external_transactions(self, month: date, user: UserType) -> QuerySet[Any]:
        dates = get_start_end_date_from(month)
        return self.get_user_queryset(user).filter(
            other_party__is_user_owner=False, date__gte=dates[0], date__lte=dates[1]
        )

    def top_expenses(self, month: date, user: UserType) -> QuerySet[Any]:
        dates = get_start_end_date_from(month)
        return (
            self.get_queryset_external_transactions(month, user)
            .filter(amount__lt=0)
            .order_by("amount")[:5]
        )

    def top_incomes(self, month: date, user: UserType) -> QuerySet[Any]:
        dates = get_start_end_date_from(month)
        return (
            self.get_queryset_external_transactions(month, user)
            .filter(
                amount__gt=0,
                other_party__is_user_owner=False,
                date__gte=dates[0],
                date__lte=dates[1],
            )
            .order_by("-amount")[:5]
        )

    def get_external_totals(self, month: date, user: UserType) -> Dict[str, Decimal]:
        dates = get_start_end_date_from(month)
        expenses = Sum("amount", filter=Q(amount__lt=0))
        incomes = Sum("amount", filter=Q(amount__gt=0))
        return self.get_queryset_external_transactions(month, user).aggregate(
            expenses=expenses, incomes=incomes
        )