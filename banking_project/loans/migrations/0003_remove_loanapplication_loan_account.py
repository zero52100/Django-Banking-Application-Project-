# Generated by Django 5.0.3 on 2024-05-07 18:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0002_loanapplication_loan_account_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loanapplication',
            name='loan_account',
        ),
    ]
