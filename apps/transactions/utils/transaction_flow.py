from decimal import Decimal
from typing import Any, Dict, List

from networkx import DiGraph, simple_cycles

from apps.transactions.models import Account, Transaction
from apps.transactions.utils.graph import Graph
from apps.transactions.utils.objects import CommonEqualityMixin


class TransactionNode(CommonEqualityMixin):
    def __init__(self, name: str):
        self.name = name


class TransactionLink(CommonEqualityMixin):
    def __init__(self, source: str, target: str, value: Decimal):
        self.source = source
        self.target = target
        self.value = value

    def has_same_target(self, target: str, source: str) -> bool:
        """we need to know if we need to flip"""
        return self.source == source and self.target == target

    def is_opposite_target(self, target: str, source: str) -> bool:
        """we need to know if we need to flip"""
        return self.source == target and self.target == source

    def update(self, value: Decimal) -> None:
        """Not only updates the moneys, but alsof flips source and target when negative moneys.
        Negative moneys is not supported in a sankey (well, I don't want it :D)"""
        self.value += value

        if self.value < 0:
            new_target = self.source
            self.source = self.target
            self.target = new_target
            self.value = Decimal.copy_abs(self.value)


class TransactionFlow:
    def __init__(self, nodes: List[TransactionNode], links: List[TransactionLink]):
        self.nodes = nodes
        self.links = links


def create_flow_for(transactions: List[Transaction]) -> Dict[str, List[Dict[str, Any]]]:
    nodes = create_nodes_from(transactions)
    links = create_links_from(transactions, nodes)
    return create_flow_graph_for(nodes, links)


def create_nodes_from(transactions: List[Transaction]) -> List[TransactionNode]:
    """
    Get nodes for the sankey out of the transactions.

    Returns:
        Sorted list of dictionaries with 'name' as key

    Example:
        [{ 'name': 'Kabisa' }, { 'name': 'Betaalrekening' }]
    """
    accounts_by_name: Dict[str, List[Account]] = {}
    nodes = set()

    for transaction in transactions:
        if transaction.receiver.name not in accounts_by_name:
            accounts_by_name[transaction.receiver.name] = []

        if transaction.other_party.name not in accounts_by_name:
            accounts_by_name[transaction.other_party.name] = []

        if transaction.receiver not in accounts_by_name[transaction.receiver.name]:
            accounts_by_name[transaction.receiver.name].append(transaction.receiver)

        if transaction.other_party not in accounts_by_name[transaction.other_party.name]:
            accounts_by_name[transaction.other_party.name].append(transaction.other_party)

    for (_, account_list) in accounts_by_name.items():
        if len(account_list) > 1:
            for account in account_list:
                nodes.add(f"{account.name} ({account.account_number})")
        else:
            nodes.add(account_list[0].name)

    return [TransactionNode(n) for n in sorted(nodes)]


def create_links_from(
    transactions: List[Transaction], nodes: List[TransactionNode]
) -> List[TransactionLink]:
    """The links between flow_nodes. To see where the moneys go"""
    links: List[TransactionLink] = []
    for transaction in transactions:
        if is_internal_expense(transaction):
            continue

        receiver_name = find_node_name_by(transaction.receiver, nodes)
        other_party_name = find_node_name_by(transaction.other_party, nodes)

        if transaction.amount > 0:
            source = other_party_name
            target = receiver_name
        else:
            source = receiver_name
            target = other_party_name

        value = Decimal.copy_abs(transaction.amount)

        for link in links:
            if link.has_same_target(target, source):
                link.update(value)
                break
            elif link.is_opposite_target(target, source):
                link.update(value * -1)
                break
        else:
            links.append(TransactionLink(source, target, Decimal.copy_abs(transaction.amount)))

    return links


def find_node_name_by(account: Account, nodes: List[TransactionNode]) -> str:
    """Get either the name with account number appended or just the name of the account"""
    return next(
        (node.name for node in nodes if node.name == f"{account.name} ({account.account_number})"),
        account.name,
    )

def remove_circular_links_from(links: List[TransactionLink], transactions: List[Transaction]) -> List[Transaction]:
    dg = DiGraph()

    for link in links:
        dg.add_edge(link.source, link.target)

    sc = simple_cycles(dg)

    # TODO: So yeah, just loop through the simple cycles and remove the target:other_party transactions

    for cycle in sc:
        links_for_cycle = [l for l in links if l.source in cycle and l.target in cycle]
        ng = networkx.DiGraph()

        if len(links_for_cycle) <= 1:
            continue

        for link in links_for_cycle:
            ng.add_edge(link.source, link.target)

        is_strongy_connected = networkx.is_strongly_connected(ng)

        print(is_strongy_connected)
        # Yay, GGs :)

    pass

def create_flow_graph_for(
    nodes: List[TransactionNode], links: List[TransactionLink]
) -> Dict[str, List[Dict[str, Any]]]:
    """The totality to create a sankey diagram"""

    import networkx

    dg = networkx.DiGraph()

    for link in links:
        dg.add_edge(link.source, link.target)

    sc = networkx.simple_cycles(dg)

    # TODO: So yeah, just loop through the simple cycles and remove the target:other_party transactions

    for cycle in sc:
        links_for_cycle = [l for l in links if l.source in cycle and l.target in cycle]
        ng = networkx.DiGraph()

        if len(links_for_cycle) <= 1:
            continue

        for link in links_for_cycle:
            ng.add_edge(link.source, link.target)

        is_strongy_connected = networkx.is_strongly_connected(ng)

        print(is_strongy_connected)
        # Yay, GGs :)


    return {"nodes": [vars(node) for node in nodes], "links": [vars(link) for link in links]}


def is_internal_expense(transaction: Transaction) -> bool:
    """Check if internal expense.
    When you have internal transactions, you will have two rows in the CSV.
    If you don't handle this in the flow generation, values will be added twice,
    which we do not want"""
    return transaction.other_party.is_user_owner is True and transaction.amount < 0
