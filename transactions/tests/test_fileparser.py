from datetime import date
from decimal import Decimal
from unittest import TestCase

from transactions.tests.utils import open_test_file
from transactions.utils.fileparser import AnonymousStorageHandler, FileParser


def test_creates_transaction_from_file() -> None:
    file = open_test_file("single_dummy.csv")
    result = FileParser(AnonymousStorageHandler()).parse(file)

    assert len(result.transactions) == 1
    assert result.amount_success == 1
    assert result.amount_duplicate == 0
    assert result.amount_failed == 0

    transaction = result.transactions[0]

    assert transaction is not None
    assert transaction.date == date(2019, 9, 1)
    assert transaction.amount == Decimal("2.5")
    assert transaction.code == "NL11RABO0104955555000000000000007213"
    assert transaction.currency == "EUR"
    assert transaction.memo == "Spotify12"

    assert transaction.receiver.name == "Own account"
    assert transaction.receiver.account_number == "NL11RABO0104955555"
    assert transaction.other_party.name == "J.M.G. Kerkhoffs eo"
    assert transaction.other_party.account_number == "NL42RABO0114164838"

def test_skips_duplicate_accounts() -> None:
    file = open_test_file('duplicate_account.csv')

    result = FileParser(AnonymousStorageHandler()).parse(file)

    assert result.amount_success, 2
    assert len(result.transactions), 2
    assert len(result.accounts), 2

def test_marks_transaction_as_duplicate() -> None:
    file = open_test_file('duplicate_transaction.csv')

    result = FileParser(AnonymousStorageHandler()).parse(file)

    assert result.amount_success == 2
    assert result.amount_duplicate == 1

def test_marks_second_transaction_as_user_owner() -> None:
    file = open_test_file('is_user_owner_switch.csv')

    result = FileParser(AnonymousStorageHandler()).parse(file)

    savings_account = next(filter(lambda a: a is not None and a.name == "Savings", result.accounts), None)

    assert savings_account is not None
    if savings_account is None: raise RuntimeError()
    assert savings_account.is_user_owner == True