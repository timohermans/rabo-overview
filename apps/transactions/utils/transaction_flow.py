from decimal import Decimal
from typing import Any, Dict, List

from apps.transactions.models import Account, Transaction


class TransactionNode:
    def __init__(self, name: str):
        self.name = name


class TransactionLink:
    def __init__(self, source: str, target: str, value: Decimal):
        self.source = source
        self.target = target
        self.value = value


class TransactionFlow:
    def __init__(self, nodes: List[TransactionNode], links: List[TransactionLink]):
        self.nodes = nodes
        self.links = links


def create_flow_for(transactions: List[Transaction]) -> Dict[str, List[Dict[str, Any]]]:
    nodes = create_nodes_from(transactions)
    links = create_links_from(transactions, nodes)
    return create_flow_graph_for(nodes, links)


def create_nodes_from(transactions: List[Transaction]) -> List[Dict[str, str]]:
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

    return [{"name": n} for n in sorted(nodes)]


def create_links_from(
    transactions: List[Transaction], nodes: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """The links between flow_nodes. To see where the moneys go"""
    links: List[Dict[str, Any]] = []
    for transaction in transactions:
        if is_internal_expense(transaction):
            continue

        receiver_name = (
            next(
                (
                    node["name"]
                    for node in nodes
                    if node["name"]
                    == f"{transaction.receiver.name} ({transaction.receiver.account_number})"
                ),
                None,
            )
            or transaction.receiver.name
        )

        other_party_name = (
            next(
                (
                    node["name"]
                    for node in nodes
                    if node["name"]
                    == f"{transaction.other_party.name} ({transaction.other_party.account_number})"
                ),
                None,
            )
            or transaction.other_party.name
        )

        if transaction.amount > 0:
            source = other_party_name
            target = receiver_name
        else:
            source = receiver_name
            target = other_party_name

        value = Decimal.copy_abs(transaction.amount)

        for link in links:
            if __is_same_target_source_link(link, target, source):
                update_link_with(link, value)
                break
            elif __is_opposite_target_source_link(link, target, source):
                update_link_with(link, value * -1)
                break
        else:
            links.append(
                {
                    "source": source,
                    "target": target,
                    "value": Decimal.copy_abs(transaction.amount),
                }
            )

    return links


def __is_same_target_source_link(link: Dict[str, Any], target: str, source: str) -> bool:
    return link["source"] == source and link["target"] == target


def __is_opposite_target_source_link(link: Dict[str, Any], target: str, source: str) -> bool:
    return link["source"] == target and link["target"] == source


def update_link_with(link: Dict[str, Any], value: Decimal) -> None:
    """Not only updates the moneys, but alsof flips source and target when negative moneys.
    Negative moneys is not supported in a sankey (well, I don't want it :D)"""
    link["value"] += value

    if link["value"] < 0:
        new_target = link["source"]
        link["source"] = link["target"]
        link["target"] = new_target
        link["value"] = Decimal.copy_abs(link["value"])


def create_flow_graph_for(
    nodes: List[Dict[str, Any]], links: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """The totality to create a sankey diagram"""
    return {"nodes": nodes, "links": links}


def is_internal_expense(transaction: Transaction) -> bool:
    """Check if internal expense.
    When you have internal transactions, you will have two rows in the CSV.
    If you don't handle this in the flow generation, values will be added twice,
    which we do not want"""
    return transaction.other_party.is_user_owner is True and transaction.amount < 0
