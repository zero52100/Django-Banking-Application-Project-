# Generated by Django 5.0.3 on 2024-05-08 00:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0003_remove_loanapplication_loan_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='loanapplication',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
