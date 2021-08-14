from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

import pytest
from django.contrib.auth import get_user_model
from transactions.models import Account, Transaction
from transactions.tests.factories import UserFactory
from transactions.tests.utils import open_test_file
from transactions.utils.fileparser import FileParser, ModelStorageHandler

if TYPE_CHECKING:
    from accounts.models import User
else:
    User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def user() -> User:
    return UserFactory()


def test_creates_transaction_from_file(user: User) -> None:
    file = open_test_file("single_dummy.csv")
    result = FileParser(ModelStorageHandler(user)).parse(file)

    transaction: Optional[Transaction] = Transaction.objects.first()

    assert result.amount_success == 1
    assert result.amount_duplicate == 0
    assert result.amount_failed == 0

    assert transaction is not None
    assert transaction.date == date(2019, 9, 1)
    assert transaction.amount == Decimal("2.5")
    assert transaction.code == "NL11RABO0104955555000000000000007213"
    assert transaction.currency == "EUR"
    assert transaction.memo == "Spotify12"
    assert transaction.user.id == user.id

    assert transaction.receiver.name == "Own account"
    assert transaction.receiver.account_number == "NL11RABO0104955555"
    assert transaction.other_party.name == "J.M.G. Kerkhoffs eo"
    assert transaction.other_party.account_number == "NL42RABO0114164838"


def test_skips_duplicate_accounts(user: User) -> None:
    file = open_test_file("duplicate_account.csv")

    result = FileParser(ModelStorageHandler(user)).parse(file)

    assert result.amount_success == 2
    assert len(Transaction.objects.all()) == 2
    assert len(Account.objects.all()) == 2


def test_marks_transaction_as_duplicate(user: User) -> None:
    other_party = Account.objects.create(
        name="J.M.G. Kerkhoffs eo",
        account_number="NL42RABO0114164838",
        is_user_owner=False,
        user=user,
    )
    receiver = Account.objects.create(
        name="Own account",
        account_number="NL11RABO0104955555",
        is_user_owner=True,
        user=user,
    )
    transaction = Transaction(
        code="NL11RABO0104955555000000000000007214",
        date=date(2019, 9, 1),
        memo="Spotify12",
        amount=Decimal("2.5"),
        currency="EUR",
        receiver=receiver,
        other_party=other_party,
        user=user,
    )
    transaction.save()

    file = open_test_file("duplicate_transaction.csv")

    result = FileParser(ModelStorageHandler(user)).parse(file)

    assert result.amount_success == 2
    assert result.amount_duplicate == 1
