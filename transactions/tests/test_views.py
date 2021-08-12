from datetime import date

from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory, Client
from django.urls import reverse

from .factories import UserFactory, TransactionFactory
from .utils import open_test_file
from ..models import Transaction
from ..views import TransactionListView, UploadAnonymousTransactionsFormView, UploadTransactionsFormView

User = get_user_model()


class TransactionListViewTestCase(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.factory = RequestFactory()

    def test_user_login_required(self) -> None:
        client = Client()
        response = client.get(reverse('transactions:index'))
        self.assertEqual(302, response.status_code)

    def test_renders_200(self) -> None:
        request = self.factory.get(reverse('transactions:index'))
        request.user = self.user
        response = TransactionListView.as_view()(request)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, "No transactions yet")

    def test_filters_on_month_200(self) -> None:
        date_str = '2019-05-01'
        transaction = TransactionFactory(date=date.fromisoformat(date_str), user=self.user)
        transaction_excluded = TransactionFactory(date=date(2019, 6, 1), user=self.user)

        request = self.factory.get(f'reverse("transactions:index")?month={date_str}')
        request.user = self.user
        response = TransactionListView.as_view()(request)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, transaction.other_party.name)
        self.assertNotContains(response, transaction_excluded.other_party.name)

    def test_gets_previous_months_transactions_by_default(self):
        now = date.today()
        transaction = TransactionFactory(date=now - relativedelta(months=1), user=self.user)
        transaction_excluded = TransactionFactory(date=now, user=self.user)
        request = self.factory.get(reverse('transactions:index'))
        request.user = self.user

        response = TransactionListView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, transaction.other_party.name)
        self.assertNotContains(response, transaction_excluded.other_party.name)

    def test_gets_only_user_owned_transactions(self):
        now = date.today() - relativedelta(months=1)
        transaction = TransactionFactory(date=now, user=self.user)
        transaction_excluded = TransactionFactory(date=now)
        request = self.factory.get(reverse('transactions:index'))
        request.user = self.user

        response = TransactionListView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, transaction.other_party.name)
        self.assertNotContains(response, transaction_excluded.other_party.name)


class UploadTransactionsFormViewTestCase(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.factory = RequestFactory()

    def test_redirects_after_successful_upload(self):
        post_data = {'file': open_test_file('single_dummy.csv')}
        request = self.factory.post(reverse('transactions:upload'), data=post_data)
        request.user = self.user

        response = UploadTransactionsFormView.as_view()(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(f'{response.url}/', reverse('transactions:index'))
        self.assertEqual(len(Transaction.objects.all()), 1)

    def test_returns_when_file_is_faulty(self):
        post_data = {'file': open_test_file('data.rtf')} 
        request = self.factory.post(reverse('transactions:upload'), data=post_data)
        request.user = self.user

        response = UploadTransactionsFormView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'File extension “rtf” is not allowed')

    def test_must_be_logged_in(self):
        c = Client()

        response = c.post(reverse('transactions:upload'), data={})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/accounts/login/?next=/transactions/upload/')

class UploadTransactionsAnonymousFormViewTestCase(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_shows_results_after_successful_parse(self):
        post_data = {'file': open_test_file('single_dummy.csv')}
        request = self.factory.post(reverse('transactions:upload-anonymous'), data=post_data)

        response = UploadAnonymousTransactionsFormView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Transaction.objects.all()), 0)
        self.assertContains(response, "Kerkhoffs")

#     def test_returns_when_file_is_faulty(self):
#         post_data = {'file': open_test_file('data.rtf')}
#         request = self.factory.post(reverse('transactions:upload-anonymous'), data=post_data)

#         response = UploadAnonymousTransactionsFormView.as_view()(request)

#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, 'File extension “rtf” is not allowed')

#     def test_returns_error_when_more_than_one_month_is_uploaded(self):
#         pass
