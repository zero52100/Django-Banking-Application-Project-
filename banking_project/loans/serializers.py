

from rest_framework import serializers
from .models import LoanType,LoanApplication

class LoanTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanType
        fields = '__all__'


class LoanApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanApplication
        fields = ['id', 'user', 'loan_type', 'amount', 'status', 'loan_account_number', 'branch_id', 'outstanding_balance']
        read_only_fields = ['id', 'user', 'status', 'outstanding_balance','branch_id','loan_account_number']

class LoanApprovalSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    loan_application_id = serializers.IntegerField()