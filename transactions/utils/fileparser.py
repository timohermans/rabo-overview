from datetime import date
from decimal import Decimal
from enum import Enum
from transactions.models import Account, Transaction
from typing import Any, Dict, List, Protocol, Optional, TYPE_CHECKING

from django.contrib.auth import get_user_model

from .file import read_raw_transaction_data_from

if TYPE_CHECKING:
    from accounts.models import User as UserType

User = get_user_model()


class ParseResult(Enum):
    SUCCESS = 1
    DUPLICATE = 2
    ERROR = 3


class CreationReport:
    def __init__(self) -> None:
        self.amount_success = 0
        self.amount_duplicate = 0
        self.amount_failed = 0
        self.transactions: List[Transaction] = [] 
        self.accounts: List[Account] = []


class StorageHandler(Protocol):
    def does_transaction_already_exist(self, transaction_code: str) -> bool: ...
    def get_account_by(self, account_number: str) -> Optional[Account]: ...
    def update_receiver(self, receiver: Account) -> Account: ...
    def create_account(self, **kwargs: Any) -> Account: ...
    def create_transaction(self, **kwargs: Any) -> Transaction: ...
        

class AnonymousStorageHandler:
    def __init__(self) -> None:
        self.account = Account
        self.transaction = Transaction
        self.accounts: List[Account] = []
        self.transactions: List[Transaction] = []

    def does_transaction_already_exist(self, transaction_code: str) -> bool:
        return next(
            filter(lambda t: t.code == transaction_code, self.transactions), None
        ) != None

    def get_account_by(self, account_number: str) -> Optional[Account]:
        return next(
            filter(lambda a: a is not None and a.account_number == account_number, self.accounts), None
        )

    def update_receiver(self, receiver: Account) -> Account:
        receiver.is_user_owner = True
        return receiver

    def create_account(self, **kwargs: dict[str, Any]) -> Account:
        account = self.account(**kwargs)
        self.accounts.append(account)
        return account

    def create_transaction(self, **kwargs: dict[str, Any]) -> Transaction:
        transaction = self.transaction(**kwargs)
        self.transactions.append(transaction)
        return transaction


class ModelStorageHandler:
    def __init__(self, user: UserType) -> None:
        self.user = user
        self.account = Account
        self.transaction = Transaction

    def does_transaction_already_exist(self, transaction_code: str) -> bool:
        return (
            len(self.transaction.objects.filter(code=transaction_code, user=self.user))
            > 0
        )

    def get_account_by(self, account_number: str) -> Optional[Account]:
        account = self.account.objects.filter(
            account_number=account_number, user=self.user
        )
        return account[0] if account else None

    def update_receiver(self, receiver: Account) -> Account:
        if not receiver.is_user_owner:
            receiver.is_user_owner = True
            receiver.save()
        return receiver

    def create_account(self, **kwargs: dict[str, Any]) -> Account:
        account = self.account(**kwargs, user=self.user)
        account.save()
        return account

    def create_transaction(self, **kwargs: dict[str, Any]) -> Transaction:
        transaction = self.transaction(**kwargs, user=self.user)
        transaction.save()
        return transaction


class FileParser:
    def __init__(self, storage_handler: StorageHandler) -> None:
        self.storage = storage_handler

    def parse(self, file: Any) -> CreationReport:
        results = [
            self.__create_transaction_from(transaction_map)
            for transaction_map in read_raw_transaction_data_from(file)
        ]

        return self.__create_result_report_from(results)

    def __create_transaction_from(self, transaction_map: Dict[str, str]) -> ParseResult:
        transaction_code = self.__map_raw_data_to_transaction_code(transaction_map)

        if self.storage.does_transaction_already_exist(transaction_code):
            return ParseResult.DUPLICATE

        receiver = self.__get_or_create_receiver(transaction_map)
        other_party = self.__get_or_create_other_party(transaction_map)
        self.__create_transaction(transaction_map, receiver, other_party)
        return ParseResult.SUCCESS

    def __map_raw_data_to_transaction_code(self, raw_map: Dict[str, str]) -> str:
        return raw_map["IBAN/BBAN"] + raw_map["Volgnr"]

    def __get_or_create_receiver(self, raw_map: Dict[str, str]) -> Account:
        receiver_kwargs: dict[str, Any] = {
            "name": "Own account",
            "account_number": raw_map["IBAN/BBAN"],
            "is_user_owner": True,
        }
        receiver = self.storage.get_account_by(receiver_kwargs["account_number"])
        return (
            self.storage.update_receiver(receiver)
            if receiver
            else self.storage.create_account(**receiver_kwargs)
        )

    def __get_or_create_other_party(self, raw_map: Dict[str, str]) -> Account:
        other_party_kwargs: dict[str, Any] = {
            "name": raw_map["Naam tegenpartij"],
            "account_number": raw_map["Tegenrekening IBAN/BBAN"],
            "is_user_owner": False,
        }
        other_party = self.storage.get_account_by(other_party_kwargs["account_number"])
        return (
            other_party
            if other_party
            else self.storage.create_account(**other_party_kwargs)
        )

    def __create_transaction(self, raw_map: Dict[str, str], receiver: Account, other_party: Account) -> Transaction:
        transaction = self.storage.create_transaction(
            date=date.fromisoformat(raw_map["Datum"]),
            code=self.__map_raw_data_to_transaction_code(raw_map),
            currency=raw_map["Munt"],
            memo=f'{raw_map["Omschrijving-1"]}{raw_map["Omschrijving-2"]}{raw_map["Omschrijving-3"]}',
            amount=Decimal(raw_map["Bedrag"].replace(",", ".")),
            receiver=receiver,
            other_party=other_party,
        )
        return transaction

    def __create_result_report_from(self, results: List[ParseResult]) -> CreationReport:
        report = CreationReport()

        for parse_result in results:
            if parse_result == ParseResult.SUCCESS:
                report.amount_success += 1
            elif parse_result == ParseResult.DUPLICATE:
                report.amount_duplicate += 1

        report.transactions = getattr(self.storage, "transactions", [])
        report.accounts = getattr(self.storage, "accounts", [])

        return report
