from apps.transactions.models import Account
from apps.transactions.templatetags.filters import filter_receivers


def test_receivers_filters_receivers_from_accounts() -> None:
    accounts = [
        Account(name="Ikea", account_number="123", is_user_owner=False),
        Account(name="Betaalrekening", account_number="1234", is_user_owner=True),
        Account(name="Spaarrekening", account_number="12345", is_user_owner=True),
        Account(name="Beter Bed", account_number="123456", is_user_owner=False),
    ]

    receivers = filter_receivers(accounts)

    assert len(receivers) == 2
    assert len([r for r in receivers if r.name == "Betaalrekening"]) == 1
    assert len([r for r in receivers if r.name == "Spaarrekening"]) == 1
