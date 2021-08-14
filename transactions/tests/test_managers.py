from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

import pytest
from django.contrib.auth import get_user_model
from transactions.models import Account, Transaction
from transactions.tests.factories import (
    AccountFactory,
    OtherPartyFactory,
    ReceiverFactory,
    TransactionFactory,
    UserFactory,
)

if TYPE_CHECKING:
    from accounts.models import User
else:
    User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def user() -> User:
    return UserFactory()


def test_gets_user_owned_top_incomes(user: User) -> None:
    receiver = ReceiverFactory(user=user)
    other_party = OtherPartyFactory(user=user)
    paying_account = OtherPartyFactory(user=user, is_user_owner=True)
    TransactionFactory(
        date=date(2021, 6, 1),
        receiver=receiver,
        other_party=other_party,
        amount=Decimal("20"),
    )
    TransactionFactory(
        date=date(2021, 6, 1),
        receiver=receiver,
        other_party=other_party,
        amount=Decimal("-20"),
    )

    incomes = Transaction.statistics.top_incomes(date(2021, 6, 1), user)
    expenses = Transaction.statistics.top_expenses(date(2021, 6, 1), user)

    assert 0 == len(incomes)
    assert 0 == len(expenses)


def test_gets_top_incomes_sorted(user: User) -> None:
    receiver = ReceiverFactory(user=user)
    other_party = OtherPartyFactory(user=user)
    paying_account = OtherPartyFactory(user=user, is_user_owner=True)
    TransactionFactory(
        date=date(2021, 6, 10),
        user=user,
        receiver=receiver,
        other_party=other_party,
        amount=Decimal("20"),
    )
    TransactionFactory(
        date=date(2021, 6, 10),
        user=user,
        receiver=receiver,
        other_party=other_party,
        amount=Decimal("70"),
    )
    TransactionFactory(
        date=date(2021, 6, 1),
        user=user,
        receiver=receiver,
        other_party=other_party,
        amount=Decimal("470"),
    )
    TransactionFactory(
        date=date(2021, 6, 30),
        user=user,
        receiver=receiver,
        other_party=other_party,
        amount=Decimal("170"),
    )
    TransactionFactory(
        date=date(2021, 6, 20),
        user=user,
        receiver=receiver,
        other_party=other_party,
        amount=Decimal("1170"),
    )
    TransactionFactory(
        date=date(2021, 7, 1),
        user=user,
        receiver=receiver,
        other_party=other_party,
        amount=Decimal("1170"),
    )
    TransactionFactory(
        date=date(2021, 6, 11),
        user=user,
        receiver=receiver,
        other_party=other_party,
        amount=Decimal("2070"),
    )
    TransactionFactory(
        date=date(2021, 6, 1),
        user=user,
        receiver=receiver,
        other_party=paying_account,
        amount=Decimal("5070"),
    )
    TransactionFactory(
        date=date(2021, 6, 10),
        user=user,
        receiver=receiver,
        other_party=other_party,
        amount=Decimal("-70"),
    )
    TransactionFactory(
        date=date(2021, 6, 10),
        user=user,
        receiver=receiver,
        other_party=other_party,
        amount=Decimal("-25.25"),
    )
    TransactionFactory(
        date=date(2021, 6, 10),
        user=user,
        receiver=receiver,
        other_party=other_party,
        amount=Decimal("-100"),
    )

    results = Transaction.statistics.top_incomes(date(2021, 6, 1), user)
    assert 5 == len(results)
    assert Decimal("2070") == results[0].amount
    assert Decimal("1170") == results[1].amount
    assert Decimal("470") == results[2].amount
    assert Decimal("170") == results[3].amount
    assert Decimal("70") == results[4].amount


def test_gets_top_expenses(user: User) -> None:
    receiver = ReceiverFactory(user=user)
    other_party = OtherPartyFactory(user=user)
    paying_account = OtherPartyFactory(user=user, is_user_owner=True)
    TransactionFactory(
        date=date(2021, 6, 10),
        user=user,
        receiver=receiver,
        other_party=other_party,
        amount=Decimal("20"),
    )
    TransactionFactory(
        date=date(2021, 6, 1),
        user=user,
        receiver=receiver,
        other_party=other_party,
        amount=Decimal("70"),
    )
    TransactionFactory(
        date=date(2021, 6, 10),
        user=user,
        receiver=receiver,
        other_party=other_party,
        amount=Decimal("-470"),
    )
    TransactionFactory(
        date=date(2021, 6, 1),
        user=user,
        receiver=receiver,
        other_party=other_party,
        amount=Decimal("-170"),
    )
    TransactionFactory(
        date=date(2021, 6, 30),
        user=user,
        receiver=receiver,
        other_party=other_party,
        amount=Decimal("-1170"),
    )
    TransactionFactory(
        date=date(2021, 7, 1),
        user=user,
        receiver=receiver,
        other_party=other_party,
        amount=Decimal("-1170"),
    )
    TransactionFactory(
        date=date(2021, 6, 20),
        user=user,
        receiver=receiver,
        other_party=other_party,
        amount=Decimal("-2070"),
    )
    TransactionFactory(
        date=date(2021, 6, 20),
        user=user,
        receiver=receiver,
        other_party=paying_account,
        amount=Decimal("-5070"),
    )
    TransactionFactory(
        date=date(2021, 6, 10),
        user=user,
        receiver=receiver,
        other_party=other_party,
        amount=Decimal("-70"),
    )
    TransactionFactory(
        date=date(2021, 6, 10),
        user=user,
        receiver=receiver,
        other_party=other_party,
        amount=Decimal("-25.25"),
    )
    TransactionFactory(
        date=date(2021, 6, 10),
        user=user,
        receiver=receiver,
        other_party=other_party,
        amount=Decimal("-100"),
    )

    results = Transaction.statistics.top_expenses(date(2021, 6, 2), user)
    assert 5 == len(results)
    assert Decimal("-2070") == results[0].amount
    assert Decimal("-1170") == results[1].amount
    assert Decimal("-470") == results[2].amount
    assert Decimal("-170") == results[3].amount
    assert Decimal("-100") == results[4].amount


def test_gets_sum_external_expenses_and_incomes(user: User) -> None:
    user = UserFactory()
    wrong_user = UserFactory()
    month = date(2021, 6, 1)
    wrong_month = date(2021, 7, 1)
    external_party = OtherPartyFactory(is_user_owner=False, user=user)
    savings_account = AccountFactory(is_user_owner=True, user=user)
    user_bank_account = ReceiverFactory(user=user)

    # expenses that are from external sources, like shopping
    TransactionFactory(
        date=month,
        user=user,
        receiver=user_bank_account,
        other_party=external_party,
        amount=Decimal("-20"),
    )
    TransactionFactory(
        date=month,
        user=user,
        receiver=user_bank_account,
        other_party=external_party,
        amount=Decimal("-40"),
    )

    # incomes that are from external sources, like salary
    TransactionFactory(
        date=month,
        user=user,
        receiver=user_bank_account,
        other_party=external_party,
        amount=Decimal("4000"),
    )
    TransactionFactory(
        date=month,
        user=user,
        receiver=user_bank_account,
        other_party=external_party,
        amount=Decimal("2500"),
    )

    # transactions that shouldn't be summed,
    # e.g. wrong month, user or transactions to your savings account
    TransactionFactory(
        date=month,
        user=user,
        receiver=user_bank_account,
        other_party=savings_account,
        amount=Decimal("-400"),
    )
    TransactionFactory(
        date=month,
        user=wrong_user,
        receiver=user_bank_account,
        other_party=external_party,
        amount=Decimal("-600"),
    )
    TransactionFactory(
        date=wrong_month,
        user=user,
        receiver=user_bank_account,
        other_party=external_party,
        amount=Decimal("-700"),
    )

    # act
    overview = Transaction.statistics.get_external_totals(month, user)

    assert Decimal("-60") == overview["expenses"]
    assert Decimal("6500") == overview["incomes"]


# def test_gets_sum_external_incomes():
# pass
