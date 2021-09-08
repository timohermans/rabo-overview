from decimal import Decimal

from apps.transactions.tests.factories import (
    OtherPartyFactory,
    ReceiverFactory,
    TransactionFactory,
)
from apps.transactions.utils.summary import Summary


def test_summary_create_flow_graph() -> None:
    """The totality of a flow graph"""
    shopping = OtherPartyFactory.build(name="Hema")
    checkings = ReceiverFactory.build(name="Betaalrekening")
    transactions = [
        TransactionFactory.build(receiver=checkings, other_party=shopping, amount=Decimal(-100)),
        TransactionFactory.build(receiver=checkings, other_party=shopping, amount=Decimal(250)),
    ]

    summary = Summary(transactions)

    assert summary.flow_graph == {
        "nodes": [{"name": "Betaalrekening"}, {"name": "Hema"}],
        "links": [{"source": "Hema", "target": "Betaalrekening", "value": Decimal(150)}],
    }
