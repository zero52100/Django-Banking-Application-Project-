from rest_framework import serializers
from .models import Branch,AccountType,BankStaff, Account,Deposit,UserDeposit
from loans.models import LoanType,LoanApplication
import re
from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 5  # Number of loans/deposits per page
    page_size_query_param = 'page_size'
    max_page_size = 1000
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
    


class DepositCreationSerializer(serializers.Serializer):
    class Meta:
        model = Deposit
        fields = ['deposit_type', 'amount']
    

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
class LoanTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanType
        fields = '__all__'
class LoanApplicationSerializer(serializers.ModelSerializer):
    loan_type_name = serializers.SerializerMethodField()

    class Meta:
        model = LoanApplication
        fields = ['id', 'loan_type', 'loan_type_name','status', 'amount', 'outstanding_balance']

    def get_loan_type_name(self, obj):
        return obj.loan_type.name if obj.loan_type else None
class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = ('id', 'deposit_type', 'interest_rate')

class UserDepositSerializer(serializers.ModelSerializer):
    deposit_details = DepositSerializer(source='deposit_type', read_only=True)

    class Meta:
        model = UserDeposit
        fields = ('id', 'deposit_details', 'amount', 'created_at', 'current_value', 'status', 'deposit_number')
class AccounDashboardSerializer(serializers.ModelSerializer):
    branch_name = serializers.SerializerMethodField()
    account_variant_name = serializers.SerializerMethodField()
    branch_ifsc_code=serializers.SerializerMethodField()
    account_holder_name=serializers.SerializerMethodField()
    account_holder_email=serializers.SerializerMethodField()
    loans = serializers.SerializerMethodField()
    deposits = serializers.SerializerMethodField()
    class Meta:
        model = Account
        fields = ('account_holder_name','account_holder_email','account_number',  'account_balance', 'status', 'interest_rate',   'branch_name', 'account_variant_name','branch_ifsc_code','loans','deposits')
        

    def get_branch_name(self, obj):
        return obj.branch.branch_name if obj.branch else None
    def get_branch_ifsc_code(self, obj):
        return obj.branch.ifsc_code if obj.branch else None
    def get_account_variant_name(self, obj):
        return obj.account_variant.account_subtype if obj.account_variant else None
    def get_account_holder_name(self, obj):
        return obj.user.full_name if obj.user else None
    def get_account_holder_email(self, obj):
        return obj.user.email if obj.user else None
    def get_loans(self, obj):
        
        loans = LoanApplication.objects.filter(user=obj.user)
        serializer = LoanApplicationSerializer(instance=loans, many=True)
        return serializer.data
    def get_deposits(self, obj):
        deposits = UserDeposit.objects.filter(user=obj.user)
        serializer = UserDepositSerializer(instance=deposits, many=True)
        return serializer.data
    



    