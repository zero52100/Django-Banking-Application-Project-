# Generated by Django 5.0.3 on 2024-05-07 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='account_balance',
            field=models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=15, null=True),
        ),
    ]