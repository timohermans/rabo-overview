from decimal import Decimal
from typing import Iterable, List

from apps.transactions.models import Account, Transaction

from .transaction_flow import create_flow_for


class Summary:
    """Summary of any list of given transactions"""

    def __init__(self, transactions: List[Transaction]) -> None:
        self.transactions_all = transactions
        if not transactions:
            return
        self.date_first = min([t.date for t in self.transactions_all])
        self.date_last = max([t.date for t in self.transactions_all])
        self.receivers = self.extract_receivers()
        self.flow_graph = create_flow_for(self.transactions_all)

    def extract_receivers(self) -> Iterable[Account]:
        """I want to have an overview of receivers as well"""
        receivers: List[Account] = []
        for transaction in self.transactions_all:
            if transaction.receiver not in receivers:
                receivers.append(transaction.receiver)
        return receivers

    @property
    def amount_of_receivers(self) -> int:
        """For display purposes you need to show the amount of receivers"""
        return sum([1 for _ in self.receivers])

    @property
    def expenses_to_outside(self) -> Decimal:
        """To whom did we donate our money?"""
        return Decimal(
            sum(
                [
                    t.amount
                    for t in self.transactions_all
                    if t.amount < 0 and not t.other_party.is_user_owner
                ]
            )
        )

    @property
    def incomes_from_outside(self) -> Decimal:
        """Who gave us their money?"""
        return Decimal(
            sum(
                [
                    t.amount
                    for t in self.transactions_all
                    if t.amount > 0 and not t.other_party.is_user_owner
                ]
            )
        )

    @property
    def total_balance(self) -> Decimal:
        """did I do good or bad this period?"""
        return self.incomes_from_outside + self.expenses_to_outside
