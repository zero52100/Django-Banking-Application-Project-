from rest_framework import serializers
from .models import SavingsGoal

class SavingsGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsGoal
        fields = ['goal_name', 'goal_amount', 'target_date']
