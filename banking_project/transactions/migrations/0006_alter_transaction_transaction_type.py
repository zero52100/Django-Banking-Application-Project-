# Generated by Django 5.0.3 on 2024-05-08 01:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0005_alter_transaction_destination_account_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(choices=[('deposit', 'Deposit'), ('withdrawal', 'Withdrawal'), ('transfer', 'Transfer'), ('loan_repayment', 'Loan Repayment'), ('processing_fee', 'Processing Fee')], max_length=20),
        ),
    ]