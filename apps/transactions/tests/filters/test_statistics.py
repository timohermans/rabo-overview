from datetime import date
from decimal import Decimal
from random import randint
from typing import List

import pytest

from apps.transactions.models import Transaction
from apps.transactions.templatetags import statistics
from apps.transactions.tests.factories import (
    OtherPartyFactory,
    ReceiverFactory,
    TransactionFactory,
    UserFactory,
)


@pytest.fixture(name="transactions")
def fixture_transactions() -> List[Transaction]:
    """Get handy prebuilt list of transactions with different accounts and amount"""
    user = UserFactory.build()
    checking_account = ReceiverFactory.build(name="Betaalrekening")
    savings_account = ReceiverFactory.build(name="Spaarrekening")
    supermarket_account = OtherPartyFactory.build(name="AH")
    electronics_account = OtherPartyFactory.build(name="Coolblue")

    transactions_built: List[Transaction] = []

    amounts = [-1000, -400, -70, -20, -10, 10, 20, 70, 400, 1000]
    possible_to_from_combinations = [
        (checking_account, savings_account),
        (savings_account, checking_account),
        (checking_account, supermarket_account),
        (checking_account, electronics_account),
    ]

    for amount in amounts:
        for (receiver, other_party) in possible_to_from_combinations:
            transactions_built.append(
                TransactionFactory.build(
                    date=date(2021, 6, randint(1, 30)),
                    user=user,
                    receiver=receiver,
                    other_party=other_party,
                    amount=Decimal(amount),
                )
            )

    return transactions_built


def test_top_external_expenses(transactions: List[Transaction]) -> None:
    """test biggest spenders"""
    results = statistics.top_expenses(transactions, 5)

    assert len(results) == 5
    assert results[0].amount == Decimal(-1000)
    assert results[1].amount == Decimal(-1000)
    assert results[2].amount == Decimal(-400)
    assert results[3].amount == Decimal(-400)
    assert results[4].amount == Decimal(-70)


def test_top_external_expenses_with_too_few_transactions(transactions: List[Transaction]) -> None:
    """don't try to fill in the expenses that aren't there"""
    results = statistics.top_expenses(transactions, 25)

    assert len(results) == 20


def test_top_external_incomes_are_sorted(transactions: List[Transaction]) -> None:
    """sort the expenses from big to small"""
    results = statistics.top_incomes(transactions, 5)

    assert len(results) == 5
    assert results[0].amount == Decimal(1000)
    assert results[1].amount == Decimal(1000)
    assert results[2].amount == Decimal(400)
    assert results[3].amount == Decimal(400)
    assert results[4].amount == Decimal(70)


def test_top_external_incomes_with_too_few_transactions(transactions: List[Transaction]) -> None:
    """Don't try to get expenses that aren't there"""
    results = statistics.top_expenses(transactions, 25)

    assert len(results) == 20


def test_summary_outgoing_totals() -> None:
    """Sums the outgoing expenses in one group"""
    checkings = ReceiverFactory.build(name="betaalrekening")
    shopping = OtherPartyFactory.build(name="albert heijn")
    transactions = [
        TransactionFactory.build(receiver=checkings, other_party=shopping, amount=Decimal(-80)),
        TransactionFactory.build(receiver=checkings, other_party=shopping, amount=Decimal(-300)),
    ]

    totals = statistics.summary(transactions)

    assert totals.expenses_to_outside == Decimal(-380)


def test_summary_outgoing_totals_0_when_no_expenses() -> None:
    """Sums the outgoing expenses in one group"""
    transactions: List[Transaction] = []

    totals = statistics.summary(transactions)

    assert totals.expenses_to_outside == Decimal(0)


def test_summary_outgoing_expenses_ignores_incomes_or_internal_transfers() -> None:
    """Only money that we actually lose needs to be tracked here"""
    work = OtherPartyFactory.build(name="kabisa")
    shopping = OtherPartyFactory.build(name="albert heijn")
    checkings = ReceiverFactory.build(name="betaalrekening")
    savings = ReceiverFactory.build(name="spaarrekening")
    transactions = [
        # should add up to all expenses
        TransactionFactory.build(receiver=checkings, other_party=shopping, amount=Decimal(-80)),
        TransactionFactory.build(receiver=checkings, other_party=shopping, amount=Decimal(-260)),
        TransactionFactory.build(receiver=savings, other_party=shopping, amount=Decimal(-40)),
        # should be ignored (to savings)
        TransactionFactory.build(receiver=checkings, other_party=savings, amount=Decimal(-100)),
        TransactionFactory.build(receiver=savings, other_party=checkings, amount=Decimal(100)),
        # should be ignored (from salary)
        TransactionFactory.build(receiver=checkings, other_party=work, amount=Decimal(1000)),
    ]

    totals = statistics.summary(transactions)

    assert totals.expenses_to_outside == Decimal(-380)


def test_summary_incomes_outside_0_when_no_incomes() -> None:
    """How much mony we got from other people, the 'got nothing' version"""
    checkings = ReceiverFactory.build()
    savings = ReceiverFactory.build()
    transactions = [
        TransactionFactory.build(receiver=checkings, other_party=savings, amount=Decimal(100)),
        TransactionFactory.build(receiver=savings, other_party=checkings, amount=Decimal(-100)),
    ]

    totals = statistics.summary(transactions)

    assert totals.incomes_from_outside == 0


def test_summary_incomes_outside_only_outside() -> None:
    """How much mony we got from other people, the 'money!' version"""
    checkings = ReceiverFactory.build()
    savings = ReceiverFactory.build()
    work = OtherPartyFactory.build()
    transactions = [
        TransactionFactory.build(receiver=checkings, other_party=savings, amount=Decimal(100)),
        TransactionFactory.build(receiver=savings, other_party=checkings, amount=Decimal(-100)),
        TransactionFactory.build(receiver=checkings, other_party=work, amount=Decimal(100)),
        TransactionFactory.build(receiver=savings, other_party=work, amount=Decimal(50)),
    ]

    totals = statistics.summary(transactions)

    assert totals.incomes_from_outside == 150


def test_summary_total_balance() -> None:
    """did I do good or bad this period?"""
    work = OtherPartyFactory.build(name="kabisa")
    shopping = OtherPartyFactory.build(name="albert heijn")
    checkings = ReceiverFactory.build(name="betaalrekening")
    savings = ReceiverFactory.build(name="spaarrekening")
    transactions = [
        # should add up to all expenses
        TransactionFactory.build(receiver=checkings, other_party=shopping, amount=Decimal(-80)),
        TransactionFactory.build(receiver=checkings, other_party=shopping, amount=Decimal(-260)),
        TransactionFactory.build(receiver=savings, other_party=shopping, amount=Decimal(-40)),
        # to savings
        TransactionFactory.build(receiver=checkings, other_party=savings, amount=Decimal(-100)),
        TransactionFactory.build(receiver=savings, other_party=checkings, amount=Decimal(100)),
        # from salary
        TransactionFactory.build(receiver=checkings, other_party=work, amount=Decimal(1000)),
    ]

    totals = statistics.summary(transactions)

    assert totals.total_balance == Decimal(620)


def test_summary_date_first_transaction() -> None:
    """When did it start?"""
    checkings = ReceiverFactory.build()
    shopping = OtherPartyFactory.build()
    transactions = [
        TransactionFactory.build(receiver=checkings, other_party=shopping, date=date(2020, 5, 10)),
        TransactionFactory.build(receiver=checkings, other_party=shopping, date=date(2020, 5, 5)),
        TransactionFactory.build(receiver=checkings, other_party=shopping, date=date(2020, 5, 20)),
    ]

    summary = statistics.summary(transactions)

    assert summary.date_first == date(2020, 5, 5)

def test_summary_date_last_transaction() -> None:
    """When did it stop?"""
    checkings = ReceiverFactory.build()
    shopping = OtherPartyFactory.build()
    transactions = [
        TransactionFactory.build(receiver=checkings, other_party=shopping, date=date(2020, 5, 10)),
        TransactionFactory.build(receiver=checkings, other_party=shopping, date=date(2020, 5, 5)),
        TransactionFactory.build(receiver=checkings, other_party=shopping, date=date(2020, 5, 20)),
    ]

    summary = statistics.summary(transactions)

    assert summary.date_last == date(2020, 5, 20)


def test_summary_amount_of_accounts() -> None:
    """Just want a nice number of accounts"""
    checkings = ReceiverFactory.build()
    savings = ReceiverFactory.build()
    shopping = OtherPartyFactory.build()
    transactions = [
        TransactionFactory.build(receiver=checkings, other_party=shopping, date=date(2020, 5, 10)),
        TransactionFactory.build(receiver=savings, other_party=shopping, date=date(2020, 5, 5)),
        TransactionFactory.build(receiver=checkings, other_party=shopping, date=date(2020, 5, 20)),
    ]

    summary = statistics.summary(transactions)

    assert summary.amount_of_receivers == 2