from decimal import Decimal
from random import randint
import factory.django
from django.contrib.auth import get_user_model

from transactions.models import Account, Transaction


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ('username',)

    username = factory.faker.Faker('user_name')
    password = factory.faker.Faker('password')


class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Account
        django_get_or_create = ('account_number',)

    name = factory.faker.Faker('name', locale='nl_NL')
    account_number = factory.faker.Faker('iban', locale='nl_NL')
    is_user_owner = False
    user = factory.SubFactory(UserFactory)


class ReceiverFactory(AccountFactory):
    is_user_owner = True


class OtherPartyFactory(AccountFactory):
    is_user_owner = False


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction
        django_get_or_create = ('code',)

    user = factory.SubFactory(UserFactory)
    receiver = factory.SubFactory(ReceiverFactory, user=factory.SelfAttribute('..user'))
    other_party = factory.SubFactory(OtherPartyFactory, user=factory.SelfAttribute('..user'))

    date = factory.Faker('date_between', start_date='-3y', end_date='today')
    currency = 'EUR'
    code = factory.LazyAttribute(lambda t: f'{t.receiver.account_number}{str(randint(1000, 999999))}')
    amount = Decimal(f'{str(randint(1, 9999))}.{str(randint(0, 99))}')
    memo = factory.Faker('sentence', nb_words=20),
