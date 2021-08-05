# Generated by Django 3.2.5 on 2021-07-25 12:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('account_number', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('code', models.CharField(max_length=36)),
                ('currency', models.CharField(max_length=3)),
                ('memo', models.TextField(null=True)),
                ('other_party', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions_sent', to='transactions.account')),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions_received', to='transactions.account')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='account',
            constraint=models.UniqueConstraint(fields=('account_number',), name='unique_account_number'),
        ),
        migrations.AddConstraint(
            model_name='transaction',
            constraint=models.UniqueConstraint(fields=('code',), name='unique_transaction_code'),
        ),
    ]
