from datetime import date
from decimal import Decimal
from enum import Enum

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum, Q

from transactions.utils import read_raw_transaction_data_from, get_start_end_date_from

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
    def __init__(self):
        super().__init__()
        from transactions.models import Account  # avoid circular reference
        self.account_model = Account

    def create_bulk_from(self, file, user) -> CreationReport:
        results = [self.__create_transaction_from(transaction_map, user)
                   for transaction_map
                   in read_raw_transaction_data_from(file)]

        return self.__create_result_report_from(results)

    def __create_transaction_from(self, transaction_map, user):
        transaction_code = self.__map_raw_data_to_transaction_code(transaction_map)

        if self.__does_transaction_already_exist(transaction_code):
            return ParseResult.DUPLICATE

        receiver = self.__get_or_create_receiver(transaction_map, user)
        other_party = self.__get_or_create_other_party(transaction_map, user)
        self.__create_transaction(transaction_map, receiver, other_party, user)
        return ParseResult.SUCCESS

    def __map_raw_data_to_transaction_code(self, raw_map):
        return raw_map['IBAN/BBAN'] + raw_map['Volgnr']

    def __does_transaction_already_exist(self, code):
        return len(super().get_queryset().filter(code=code)) > 0

    def __get_or_create_receiver(self, raw_map, user):
        receiver_kwargs = {'name': 'Own account', 'account_number': raw_map['IBAN/BBAN'], 'is_user_owner': True,
                           'user': user}
        receiver = self.account_model.objects.filter(account_number=receiver_kwargs['account_number'])
        return self.__update_receiver(receiver[0]) if receiver else self.__create_receiver(**receiver_kwargs)

    def __update_receiver(self, receiver):
        if not receiver.is_user_owner:
            receiver.is_user_owner = True
            receiver.save()
        return receiver

    def __create_receiver(self, **kwargs):
        receiver = self.account_model(**kwargs)
        receiver.save()
        return receiver

    def __get_or_create_other_party(self, raw_map, user):
        other_party_kwargs = {'name': raw_map['Naam tegenpartij'], 'account_number': raw_map['Tegenrekening IBAN/BBAN'],
                              'is_user_owner': False, 'user': user}
        other_party = self.account_model.objects.filter(account_number=other_party_kwargs['account_number'])
        return other_party[0] if other_party else self.__create_other_party(**other_party_kwargs)

    def __create_other_party(self, **kwargs):
        other_party = self.account_model(**kwargs)
        other_party.save()
        return other_party

    def __create_transaction(self, raw_map, receiver, other_party, user):
        transaction = self.model(
            date=date.fromisoformat(raw_map['Datum']),
            code=self.__map_raw_data_to_transaction_code(raw_map),
            currency=raw_map['Munt'],
            memo=f'{raw_map["Omschrijving-1"]}{raw_map["Omschrijving-2"]}{raw_map["Omschrijving-3"]}',
            amount=Decimal(raw_map['Bedrag'].replace(',', '.')),
            receiver=receiver,
            other_party=other_party,
            user=user
        )
        transaction.save()
        return transaction

    def __create_result_report_from(self, results):
        report = CreationReport()

        for parse_result in results:
            if parse_result == ParseResult.SUCCESS:
                report.amount_success += 1
            elif parse_result == ParseResult.DUPLICATE:
                report.amount_duplicate += 1

        return report


class StatisticsManager(models.Manager):
    def get_queryset(self, user: User):
        return super().get_queryset().filter(user=user)

    def get_queryset_external_transactions(self, month, user):
        dates = get_start_end_date_from(month)
        return self.get_queryset(user) \
            .filter(other_party__is_user_owner=False, date__gte=dates[0], date__lte=dates[1])

    def top_expenses(self, month: date, user: User):
        dates = get_start_end_date_from(month)
        return self.get_queryset_external_transactions(month, user) \
                   .filter(amount__lt=0) \
                   .order_by('amount')[:5]

    def top_incomes(self, month: date, user: User):
        dates = get_start_end_date_from(month)
        return self.get_queryset_external_transactions(month, user) \
                   .filter(amount__gt=0, other_party__is_user_owner=False, date__gte=dates[0], date__lte=dates[1]) \
                   .order_by('-amount')[:5]

    def get_external_totals(self, month: date, user: User) -> Decimal:
        dates = get_start_end_date_from(month)
        expenses = Sum('amount', filter=Q(amount__lt=0))
        incomes = Sum('amount', filter=Q(amount__gt=0))
        return self.get_queryset_external_transactions(month, user) \
            .aggregate(expenses=expenses, incomes=incomes)
