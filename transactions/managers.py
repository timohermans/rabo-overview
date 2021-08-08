from datetime import date
from decimal import Decimal
from enum import Enum
from transactions.utils.date import get_start_end_date_from
from transactions.utils.fileparser import FileParser, ModelStorageHandler

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum, Q

User = get_user_model()


# TODO: https://stackoverflow.com/questions/59031982/type-annotations-for-django-models
class ParseResult(Enum):
    SUCCESS = 1
    DUPLICATE = 2
    ERROR = 3


class CreationReport:
    def __init__(self):
        self.amount_success = 0
        self.amount_duplicate = 0
        self.amount_failed = 0


class CreationManager(models.Manager):
    def create_bulk_from(self, file, user) -> CreationReport:
        parser = FileParser(ModelStorageHandler(user))
        return parser.parse(file)


class StatisticsManager(models.Manager):
    def get_queryset(self, user: User):
        return super().get_queryset().filter(user=user)

    def get_queryset_external_transactions(self, month, user):
        dates = get_start_end_date_from(month)
        return self.get_queryset(user).filter(
            other_party__is_user_owner=False, date__gte=dates[0], date__lte=dates[1]
        )

    def top_expenses(self, month: date, user: User):
        dates = get_start_end_date_from(month)
        return (
            self.get_queryset_external_transactions(month, user)
            .filter(amount__lt=0)
            .order_by("amount")[:5]
        )

    def top_incomes(self, month: date, user: User):
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

    def get_external_totals(self, month: date, user: User) -> Decimal:
        dates = get_start_end_date_from(month)
        expenses = Sum("amount", filter=Q(amount__lt=0))
        incomes = Sum("amount", filter=Q(amount__gt=0))
        return self.get_queryset_external_transactions(month, user).aggregate(
            expenses=expenses, incomes=incomes
        )
