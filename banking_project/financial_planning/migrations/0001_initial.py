# Generated by Django 5.0.3 on 2024-05-08 03:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monthly_budget', models.DecimalField(decimal_places=2, max_digits=15)),
                ('total_expenses', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('withdrawal', 'Withdrawal'), ('loan_repayment', 'Loan Repayment')], max_length=100)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('date', models.DateField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SavingsGoal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('goal_name', models.CharField(max_length=100)),
                ('goal_amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('target_date', models.IntegerField()),
                ('created_date', models.DateField(auto_now_add=True)),
                ('status', models.CharField(choices=[('processing', 'Goal Processing'), ('achieved', 'Goal Achieved')], default='processing', max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
