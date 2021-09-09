from decimal import Decimal

from apps.transactions.tests.factories import (
    OtherPartyFactory,
    ReceiverFactory,
    TransactionFactory,
)
from apps.transactions.utils import transaction_flow
from apps.transactions.utils.transaction_flow import TransactionLink, TransactionNode


def test_summary_creates_unique_flow_nodes_from_transactions() -> None:
    """I want all parties involved as nodes for sankey"""
    work = OtherPartyFactory.build(name="Kabisa")
    checkings = ReceiverFactory.build(name="Betaalrekening")
    savings = ReceiverFactory.build(name="Spaarrekening")
    transactions = [
        TransactionFactory.build(receiver=checkings, other_party=work),
        TransactionFactory.build(receiver=checkings, other_party=savings, amount=Decimal(-100)),
        TransactionFactory.build(receiver=savings, other_party=checkings, amount=Decimal(100)),
    ]

    nodes = transaction_flow.create_nodes_from(transactions)

    assert nodes == [
        TransactionNode("Betaalrekening"),
        TransactionNode("Kabisa"),
        TransactionNode("Spaarrekening"),
    ]


def test_summary_flow_nodes_when_same_name_different_account_then_two_nodes() -> None:
    checkings = ReceiverFactory.build(name="Achternaam eo.", account_number="NL11RABO011")
    savings = ReceiverFactory.build(name="Achternaam eo.", account_number="NL11RABO022")
    shopping = ReceiverFactory.build(name="Albert Heijn", account_number="NL20INGB011")
    transactions = [
        TransactionFactory.build(receiver=checkings, other_party=savings, amount=Decimal(100)),
        TransactionFactory.build(receiver=savings, other_party=checkings, amount=Decimal(-100)),
        TransactionFactory.build(receiver=checkings, other_party=shopping, amount=Decimal(-50)),
    ]

    nodes = transaction_flow.create_nodes_from(transactions)

    assert nodes == [
        TransactionNode("Achternaam eo. (NL11RABO011)"),
        TransactionNode("Achternaam eo. (NL11RABO022)"),
        TransactionNode("Albert Heijn"),
    ]


def test_summary_creates_flow_link_from_single_transaction() -> None:
    """To see where the moneys go"""
    shopping = OtherPartyFactory.build(name="Hema")
    checkings = ReceiverFactory.build(name="Betaalrekening")
    transactions = [
        TransactionFactory.build(receiver=checkings, other_party=shopping, amount=Decimal(-100)),
    ]

    links = transaction_flow.create_links_from(
        transactions, transaction_flow.create_nodes_from(transactions)
    )

    assert links == [TransactionLink("Betaalrekening", "Hema", Decimal(100))]


def test_summary_flow_link_same_source_and_target_sums_values() -> None:
    """We don't want duplicate links. Just add the values"""
    shopping = OtherPartyFactory.build(name="Hema")
    checkings = ReceiverFactory.build(name="Betaalrekening")
    transactions = [
        TransactionFactory.build(receiver=checkings, other_party=shopping, amount=Decimal(-100)),
        TransactionFactory.build(receiver=checkings, other_party=shopping, amount=Decimal(-200)),
        TransactionFactory.build(receiver=checkings, other_party=shopping, amount=Decimal(25)),
    ]

    links = transaction_flow.create_links_from(
        transactions, transaction_flow.create_nodes_from(transactions)
    )

    assert links == [TransactionLink("Betaalrekening", "Hema", Decimal(275))]


def test_summary_flow_link_internal_transaction_should_sum_successful() -> None:
    """Internal transactions have two transactions, they should not be counted"""
    checkings = ReceiverFactory.build(name="Betaalrekening")
    savings = ReceiverFactory.build(name="Spaarrekening")
    transactions = [
        TransactionFactory.build(
            receiver=checkings, other_party=savings, amount=Decimal(-100), memo="Geld PB"
        ),
        TransactionFactory.build(
            receiver=savings, other_party=checkings, amount=Decimal(100), memo="Geld PB"
        ),
    ]

    links = transaction_flow.create_links_from(
        transactions, transaction_flow.create_nodes_from(transactions)
    )

    assert links[0].value == Decimal(100)


def test_summary_flow_link_same_source_and_target_flip_source_and_target_when_negative_numbers() -> None:
    """When adding values, the source and target need to flip so that value is always positive"""
    shopping = OtherPartyFactory.build(name="Hema")
    checkings = ReceiverFactory.build(name="Betaalrekening")
    transactions = [
        TransactionFactory.build(receiver=checkings, other_party=shopping, amount=Decimal(-100)),
        TransactionFactory.build(receiver=checkings, other_party=shopping, amount=Decimal(250)),
    ]

    links = transaction_flow.create_links_from(
        transactions, transaction_flow.create_nodes_from(transactions)
    )

    assert links == [TransactionLink("Hema", "Betaalrekening", Decimal(150))]


def test_summary_creates_flow_links_multiple() -> None:
    """To see where the moneys go"""
    checkings = ReceiverFactory.build(name="Eigen rekening", account_number="NL11RABO1")
    shopping = OtherPartyFactory.build(name="Hema")
    savings = ReceiverFactory.build(name="Eigen rekening", account_number="NL11RABO2")
    transactions = [
        TransactionFactory.build(receiver=checkings, other_party=shopping, amount=Decimal(-200)),
        TransactionFactory.build(receiver=checkings, other_party=savings, amount=Decimal(-100)),
        TransactionFactory.build(receiver=savings, other_party=checkings, amount=Decimal(100)),
        TransactionFactory.build(receiver=savings, other_party=checkings, amount=Decimal(500)),
        TransactionFactory.build(receiver=savings, other_party=shopping, amount=Decimal(-300)),
    ]

    links = transaction_flow.create_links_from(
        transactions, transaction_flow.create_nodes_from(transactions)
    )

    assert links == [
        TransactionLink("Eigen rekening (NL11RABO1)", "Hema", Decimal(200)),
        TransactionLink("Eigen rekening (NL11RABO1)", "Eigen rekening (NL11RABO2)", Decimal(600)),
        TransactionLink("Eigen rekening (NL11RABO2)", "Hema", Decimal(300)),
    ]


def test_summary_create_flow_graph() -> None:
    """The totality of a flow graph"""
    shopping = OtherPartyFactory.build(name="Hema")
    checkings = ReceiverFactory.build(name="Betaalrekening")
    transactions = [
        TransactionFactory.build(receiver=checkings, other_party=shopping, amount=Decimal(-100)),
        TransactionFactory.build(receiver=checkings, other_party=shopping, amount=Decimal(250)),
    ]
    nodes = transaction_flow.create_nodes_from(transactions)

    graph = transaction_flow.create_flow_graph_for(
        nodes, transaction_flow.create_links_from(transactions, nodes)
    )

    assert graph == {
        "nodes": [{"name": "Betaalrekening"}, {"name": "Hema"}],
        "links": [{"source": "Hema", "target": "Betaalrekening", "value": Decimal(150)}],
    }
