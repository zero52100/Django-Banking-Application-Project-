# Generated by Django 5.0.3 on 2024-05-06 13:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_alter_accounttype_account_subtype'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='account_type',
            new_name='account_variant',
        ),
    ]
