from apps.transactions.models import Account
from apps.transactions.templatetags import filters
from apps.transactions.tests.factories import (
    OtherPartyFactory,
    ReceiverFactory,
    TransactionFactory,
)


def test_receivers_filters_receivers_from_accounts() -> None:
    """Only receivers"""
    accounts = [
        Account(name="Ikea", account_number="123", is_user_owner=False),
        Account(name="Betaalrekening", account_number="1234", is_user_owner=True),
        Account(name="Spaarrekening", account_number="12345", is_user_owner=True),
        Account(name="Beter Bed", account_number="123456", is_user_owner=False),
    ]

    receiver_list = list(filters.receivers(accounts))

    assert len(receiver_list) == 2
    assert len([r for r in receiver_list if r.name == "Betaalrekening"]) == 1
    assert len([r for r in receiver_list if r.name == "Spaarrekening"]) == 1


def test_short_account_number_displays_last_characters() -> None:
    """It's way too hard to remember whole IBANs"""
    account_number = "NL11RABO104389104"

    actual = filters.short_account_number(account_number)

    assert actual == "NL...9104"


def test_of_receiver_filters_transactions_for_receiver() -> None:
    """Get transactions for only one receiver"""
    receiver = ReceiverFactory.build()
    wrong_receiver = ReceiverFactory.build()
    other_party = OtherPartyFactory.build()
    transactions = [
        TransactionFactory.build(receiver=wrong_receiver, other_party=other_party),
        TransactionFactory.build(receiver=wrong_receiver, other_party=other_party),
        TransactionFactory.build(receiver=receiver, other_party=other_party),
        TransactionFactory.build(receiver=wrong_receiver, other_party=other_party),
    ]

    receiver_transactions = filters.of_receiver(transactions, receiver)

    assert sum(1 for r in receiver_transactions if r.receiver == receiver) == 1

def test_get_gets_property_of_object() -> None:
    """I want properties in templates!"""
    receiver = ReceiverFactory.build()

    actual = filters.get(receiver, "name")

    assert actual == receiver.name
