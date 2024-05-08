from rest_framework import serializers
from .models import SavingsGoal,Budget,Expense

class SavingsGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsGoal
        fields = ['goal_name', 'goal_amount', 'target_date','status']


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['id', 'user', 'monthly_budget', 'remaining_budget']
        read_only_fields = ['id', 'user']

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['id', 'user', 'category', 'amount', 'date']
        read_only_fields = ['id', 'user']
