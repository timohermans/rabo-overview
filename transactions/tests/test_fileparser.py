from datetime import date
from decimal import Decimal
from unittest import TestCase

from transactions.tests.utils import open_test_file
from transactions.utils.fileparser import AnonymousStorageHandler, FileParser


class FileParserTestCase(TestCase):
    def test_creates_transaction_from_file(self) -> None:
        file = open_test_file("single_dummy.csv")
        result = FileParser(AnonymousStorageHandler()).parse(file)

        self.assertEqual(len(result.transactions), 1)
        self.assertEqual(result.amount_success, 1)
        self.assertEqual(result.amount_duplicate, 0)
        self.assertEqual(result.amount_failed, 0)

        transaction = result.transactions[0]

        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.date, date(2019, 9, 1))
        self.assertEqual(transaction.amount, Decimal("2.5"))
        self.assertEqual(transaction.code, "NL11RABO0104955555000000000000007213")
        self.assertEqual(transaction.currency, "EUR")
        self.assertEqual(transaction.memo, "Spotify12")

        self.assertEqual(transaction.receiver.name, "Own account")
        self.assertEqual(transaction.receiver.account_number, "NL11RABO0104955555")
        self.assertEqual(transaction.other_party.name, "J.M.G. Kerkhoffs eo")
        self.assertEqual(transaction.other_party.account_number, "NL42RABO0114164838")

    def test_skips_duplicate_accounts(self) -> None:
        file = open_test_file('duplicate_account.csv')

        result = FileParser(AnonymousStorageHandler()).parse(file)

        self.assertEqual(result.amount_success, 2)
        self.assertEqual(len(result.transactions), 2)
        self.assertEqual(len(result.accounts), 2)

    def test_marks_transaction_as_duplicate(self) -> None:
        file = open_test_file('duplicate_transaction.csv')

        result = FileParser(AnonymousStorageHandler()).parse(file)

        self.assertEqual(result.amount_success, 2)
        self.assertEqual(result.amount_duplicate, 1)