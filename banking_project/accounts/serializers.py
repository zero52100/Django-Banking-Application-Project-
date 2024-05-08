from rest_framework import serializers
from .models import Branch,AccountType,BankStaff, Account,Deposit
import re

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'bank_name', 'branch_name', 'bank_manager', 'ifsc_code', 'mobile_number', 'address', 'pincode', 'status']
        read_only_fields = ['ifsc_code'] 

    def validate_branch_name(self, value):
        
        if Branch.objects.filter(branch_name=value).exists():
            raise serializers.ValidationError("Branch with this name already exists.")
        return value

    def validate_mobile_number(self, value):
        
        if Branch.objects.filter(mobile_number=value).exists():
            raise serializers.ValidationError("Branch with this mobile number  already exists.")
        
        
        if len(value) != 10:
            raise serializers.ValidationError("Mobile number must be 10 digits long.")
        
        if not re.match(r"^[6-9]\d{9}$", value):
            raise serializers.ValidationError("Invalid mobile number format. Please enter a valid Indian mobile number ,should start with 6,7,8,9")
        return value
    def validate_pincode(self, value):
        
        if not re.match(r"^[1-9][0-9]{5}$", value):
            raise serializers.ValidationError("Invalid pincode format. Please enter a valid Indian pincode.")
        return value

    def create(self, validated_data):
        
        validated_data['ifsc_code'] = self.generate_ifsc_code()
       
        while Branch.objects.filter(ifsc_code=validated_data['ifsc_code']).exists():
            validated_data['ifsc_code'] = self.generate_ifsc_code()
        branch = Branch.objects.create(**validated_data)
        return branch

    def generate_ifsc_code(self):
        
        import random
        numbers = ''.join(str(random.randint(0, 9)) for _ in range(7))
        return 'ABC' + numbers

class AccountTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=AccountType
        fields = [
            'id','account_type', 'account_subtype', 'minimum_balance',
            'interest_rate', 'senior_citizen_interest_rate', 'monthly_transaction_limit',
             'additional_atm_charge',
            'debit_card_yearly_fee','free_atm_withdrawals'
            
        ]

class DespositTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = [
            'id', 'deposit_type', 'interest_rate', 'created_at'
        ]

class BankStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankStaff
        fields = '__all__'

    def validate_user(self, value):
        
        if value.user_type != 'staff' or not value.is_active:
            raise serializers.ValidationError("The user must have user_type='staff' and be active.")
        return value
    
class AccountCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['account_variant', 'branch']
    def validate_user(self, value):
       
        if value.user_type != 'customer' or not value.is_active:
            raise serializers.ValidationError("The user must have user_type='customer' and be active.")
        return value
    

        