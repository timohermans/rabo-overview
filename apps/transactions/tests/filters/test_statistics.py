from datetime import date
from decimal import Decimal
from random import randint
from typing import List

import pytest
from apps.transactions.models import Transaction
from apps.transactions.templatetags.statistics import top_expenses, top_incomes
from apps.transactions.tests.factories import (OtherPartyFactory, ReceiverFactory,
                                          TransactionFactory, UserFactory)


@pytest.fixture
def transactions() -> List[Transaction]:
    user = UserFactory.build()
    checking_account = ReceiverFactory.build(name="Betaalrekening")
    savings_account = ReceiverFactory.build(name="Spaarrekening")
    supermarket_account = OtherPartyFactory.build(name="AH")
    electronics_account = OtherPartyFactory.build(name="Coolblue")

    transactions: List[Transaction] = []

    amounts = [-1000, -400, -70, -20, -10, 10, 20, 70, 400, 1000]
    possible_to_from_combinations = [
        (checking_account, savings_account),
        (savings_account, checking_account),
        (checking_account, supermarket_account),
        (checking_account, electronics_account),
    ]

    for amount in amounts:
        for (receiver, other_party) in possible_to_from_combinations:
            transactions.append(
                TransactionFactory.build(
                    date=date(2021, 6, randint(1, 30)),
                    user=user,
                    receiver=receiver,
                    other_party=other_party,
                    amount=Decimal(amount),
                )
            )

    return transactions


def test_top_external_expenses(transactions: List[Transaction]) -> None:
    results = top_expenses(transactions, 5)

    assert len(results) == 5
    assert results[0].amount == Decimal(-1000)
    assert results[1].amount == Decimal(-1000)
    assert results[2].amount == Decimal(-400)
    assert results[3].amount == Decimal(-400)
    assert results[4].amount == Decimal(-70)

def test_top_external_expenses_with_too_few_transactions(transactions: List[Transaction]) -> None:
    results = top_expenses(transactions, 25)

    assert len(results) == 20

def test_top_external_incomes_are_sorted(transactions: List[Transaction]) -> None:
    results = top_incomes(transactions, 5)

    assert len(results) == 5
    assert results[0].amount == Decimal(1000)
    assert results[1].amount == Decimal(1000)
    assert results[2].amount == Decimal(400)
    assert results[3].amount == Decimal(400)
    assert results[4].amount == Decimal(70)


def test_top_external_incomes_with_too_few_transactions(transactions: List[Transaction]) -> None:
    results = top_expenses(transactions, 25)

    assert len(results) == 20