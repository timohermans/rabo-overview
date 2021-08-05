from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from transactions.models import Transaction, Account
from transactions.tests.factories import UserFactory, AccountFactory, TransactionFactory, OtherPartyFactory, \
    ReceiverFactory
from transactions.tests.utils import open_test_file

User = get_user_model()


class TransactionTestCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='12345')
        pass

    def test_creates_transaction_from_file(self):
        file = open_test_file('single_dummy.csv')
        result = Transaction.creators.create_bulk_from(file, self.user)

        transaction = Transaction.objects.first()

        self.assertEqual(result.amount_success, 1)
        self.assertEqual(result.amount_duplicate, 0)
        self.assertEqual(result.amount_failed, 0)

        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.date, date(2019, 9, 1))
        self.assertEqual(transaction.amount, Decimal('2.5'))
        self.assertEqual(transaction.code, 'NL11RABO0104955555000000000000007213')
        self.assertEqual(transaction.currency, 'EUR')
        self.assertEqual(transaction.memo, 'Spotify12')
        self.assertEqual(transaction.user.id, self.user.id)

        self.assertEqual(transaction.receiver.name, 'Own account')
        self.assertEqual(transaction.receiver.account_number, 'NL11RABO0104955555')
        self.assertEqual(transaction.other_party.name, 'J.M.G. Kerkhoffs eo')
        self.assertEqual(transaction.other_party.account_number, 'NL42RABO0114164838')

    def test_skips_duplicate_accounts(self):
        file = open_test_file('duplicate_account.csv')

        result = Transaction.creators.create_bulk_from(file, self.user)

        self.assertEqual(result.amount_success, 2)
        self.assertEqual(len(Transaction.objects.all()), 2)
        self.assertEqual(len(Account.objects.all()), 2)

    def test_marks_transaction_as_duplicate(self):
        other_party = Account.objects.create(name='J.M.G. Kerkhoffs eo', account_number='NL42RABO0114164838',
                                             is_user_owner=False, user=self.user)
        receiver = Account.objects.create(name='Own account', account_number='NL11RABO0104955555',
                                          is_user_owner=True, user=self.user)
        transaction = Transaction(
            code='NL11RABO0104955555000000000000007214',
            date=date(2019, 9, 1),
            memo='Spotify12',
            amount=Decimal('2.5'),
            currency='EUR',
            receiver=receiver,
            other_party=other_party,
            user=self.user
        )
        transaction.save()

        file = open_test_file('duplicate_transaction.csv')

        result = Transaction.creators.create_bulk_from(file, self.user)

        self.assertEqual(result.amount_success, 2)
        self.assertEqual(result.amount_duplicate, 1)


class TransactionStatisticsTestCase(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()

    def test_gets_user_owned_top_incomes(self):
        receiver = ReceiverFactory(user=self.user)
        other_party = OtherPartyFactory(user=self.user)
        paying_account = OtherPartyFactory(user=self.user, is_user_owner=True)
        TransactionFactory(date=date(2021, 6, 1), receiver=receiver, other_party=other_party, amount=Decimal('20'))
        TransactionFactory(date=date(2021, 6, 1), receiver=receiver, other_party=other_party, amount=Decimal('-20'))

        incomes = Transaction.statistics.top_incomes(date(2021, 6, 1), self.user)
        expenses = Transaction.statistics.top_expenses(date(2021, 6, 1), self.user)

        self.assertEqual(0, len(incomes))
        self.assertEqual(0, len(expenses))

    def test_gets_top_incomes_sorted(self):
        receiver = ReceiverFactory(user=self.user)
        other_party = OtherPartyFactory(user=self.user)
        paying_account = OtherPartyFactory(user=self.user, is_user_owner=True)
        TransactionFactory(date=date(2021, 6, 10), user=self.user, receiver=receiver, other_party=other_party,
                           amount=Decimal('20'))
        TransactionFactory(date=date(2021, 6, 10), user=self.user, receiver=receiver, other_party=other_party,
                           amount=Decimal('70'))
        TransactionFactory(date=date(2021, 6, 1), user=self.user, receiver=receiver, other_party=other_party,
                           amount=Decimal('470'))
        TransactionFactory(date=date(2021, 6, 30), user=self.user, receiver=receiver, other_party=other_party,
                           amount=Decimal('170'))
        TransactionFactory(date=date(2021, 6, 20), user=self.user, receiver=receiver, other_party=other_party,
                           amount=Decimal('1170'))
        TransactionFactory(date=date(2021, 7, 1), user=self.user, receiver=receiver, other_party=other_party,
                           amount=Decimal('1170'))
        TransactionFactory(date=date(2021, 6, 11), user=self.user, receiver=receiver, other_party=other_party,
                           amount=Decimal('2070'))
        TransactionFactory(date=date(2021, 6, 1), user=self.user, receiver=receiver, other_party=paying_account,
                           amount=Decimal('5070'))
        TransactionFactory(date=date(2021, 6, 10), user=self.user, receiver=receiver, other_party=other_party,
                           amount=Decimal('-70'))
        TransactionFactory(date=date(2021, 6, 10), user=self.user, receiver=receiver, other_party=other_party,
                           amount=Decimal('-25.25'))
        TransactionFactory(date=date(2021, 6, 10), user=self.user, receiver=receiver, other_party=other_party,
                           amount=Decimal('-100'))

        results = Transaction.statistics.top_incomes(date(2021, 6, 1), self.user)
        self.assertEqual(5, len(results))
        self.assertEqual(Decimal('2070'), results[0].amount)
        self.assertEqual(Decimal('1170'), results[1].amount)
        self.assertEqual(Decimal('470'), results[2].amount)
        self.assertEqual(Decimal('170'), results[3].amount)
        self.assertEqual(Decimal('70'), results[4].amount)

    def test_gets_top_expenses(self):
        receiver = ReceiverFactory(user=self.user)
        other_party = OtherPartyFactory(user=self.user)
        paying_account = OtherPartyFactory(user=self.user, is_user_owner=True)
        TransactionFactory(date=date(2021, 6, 10), user=self.user, receiver=receiver, other_party=other_party,
                           amount=Decimal('20'))
        TransactionFactory(date=date(2021, 6, 1), user=self.user, receiver=receiver, other_party=other_party,
                           amount=Decimal('70'))
        TransactionFactory(date=date(2021, 6, 10), user=self.user, receiver=receiver, other_party=other_party,
                           amount=Decimal('-470'))
        TransactionFactory(date=date(2021, 6, 1), user=self.user, receiver=receiver, other_party=other_party,
                           amount=Decimal('-170'))
        TransactionFactory(date=date(2021, 6, 30), user=self.user, receiver=receiver, other_party=other_party,
                           amount=Decimal('-1170'))
        TransactionFactory(date=date(2021, 7, 1), user=self.user, receiver=receiver, other_party=other_party,
                           amount=Decimal('-1170'))
        TransactionFactory(date=date(2021, 6, 20), user=self.user, receiver=receiver, other_party=other_party,
                           amount=Decimal('-2070'))
        TransactionFactory(date=date(2021, 6, 20), user=self.user, receiver=receiver, other_party=paying_account,
                           amount=Decimal('-5070'))
        TransactionFactory(date=date(2021, 6, 10), user=self.user, receiver=receiver, other_party=other_party,
                           amount=Decimal('-70'))
        TransactionFactory(date=date(2021, 6, 10), user=self.user, receiver=receiver, other_party=other_party,
                           amount=Decimal('-25.25'))
        TransactionFactory(date=date(2021, 6, 10), user=self.user, receiver=receiver, other_party=other_party,
                           amount=Decimal('-100'))

        results = Transaction.statistics.top_expenses(date(2021, 6, 2), self.user)
        self.assertEqual(5, len(results))
        self.assertEqual(Decimal('-2070'), results[0].amount)
        self.assertEqual(Decimal('-1170'), results[1].amount)
        self.assertEqual(Decimal('-470'), results[2].amount)
        self.assertEqual(Decimal('-170'), results[3].amount)
        self.assertEqual(Decimal('-100'), results[4].amount)

    def test_gets_sum_external_expenses_and_incomes(self):
        user = UserFactory()
        wrong_user = UserFactory()
        month = date(2021, 6, 1)
        wrong_month = date(2021, 7, 1)
        external_party = OtherPartyFactory(is_user_owner=False, user=user)
        savings_account = AccountFactory(is_user_owner=True, user=user)
        user_bank_account = ReceiverFactory(user=user)

        # expenses that are from external sources, like shopping
        TransactionFactory(date=month, user=user, receiver=user_bank_account, other_party=external_party,
                           amount=Decimal('-20'))
        TransactionFactory(date=month, user=user, receiver=user_bank_account, other_party=external_party,
                           amount=Decimal('-40'))

        # incomes that are from external sources, like salary
        TransactionFactory(date=month, user=user, receiver=user_bank_account, other_party=external_party,
                           amount=Decimal('4000'))
        TransactionFactory(date=month, user=user, receiver=user_bank_account, other_party=external_party,
                           amount=Decimal('2500'))

        # transactions that shouldn't be summed,
        # e.g. wrong month, user or transactions to your savings account
        TransactionFactory(date=month, user=user, receiver=user_bank_account, other_party=savings_account,
                           amount=Decimal('-400'))
        TransactionFactory(date=month, user=wrong_user, receiver=user_bank_account, other_party=external_party,
                           amount=Decimal('-600'))
        TransactionFactory(date=wrong_month, user=user, receiver=user_bank_account, other_party=external_party,
                           amount=Decimal('-700'))

        # act
        overview = Transaction.statistics.get_external_totals(month, user)

        self.assertEqual(Decimal('-60'), overview['expenses'])
        self.assertEqual(Decimal('6500'), overview['incomes'])

    def test_gets_sum_external_incomes(self):
        pass
