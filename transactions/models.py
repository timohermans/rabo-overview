from django.contrib.auth import get_user_model
from django.db import models

from transactions.managers import StatisticsManager

User = get_user_model()


class Account(models.Model):
    name = models.CharField(max_length=70)
    account_number = models.CharField(max_length=36)
    is_user_owner = models.BooleanField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['account_number'], name='unique_account_number')]


class Transaction(models.Model):
    objects = models.Manager()
    statistics = StatisticsManager()

    date = models.DateField()
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    code = models.CharField(max_length=36)
    currency = models.CharField(max_length=3)
    memo = models.TextField(null=True, blank=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    receiver = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions_received')
    other_party = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions_sent')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['code'], name='unique_transaction_code')]
