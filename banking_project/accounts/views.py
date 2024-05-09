from rest_framework import generics, permissions, status
from datetime import datetime, timedelta
from rest_framework.response import Response
from transactions.models import Transaction
from django.db import transaction
from .models import Account, AccountType, Branch, BankStaff,Deposit,UserDeposit
from .serializers import BranchSerializer,AccountTypeSerializer,BankStaffSerializer,AccountCreationSerializer,DespositTypeSerializer,DepositCreationSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from rest_framework.views import APIView
import random
from django.core.mail import send_mail
from django.conf import settings
from utilities.notifications import send_balance_notification,send_email

class BranchPagination(PageNumberPagination):
    page_size = 3
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 100

class BranchListCreateAPIView(generics.ListCreateAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = BranchPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['branch_name', 'bank_name','status','ifsc_code','id']
    ordering_fields = ['branch_name', 'bank_name','status','ifsc_code','id']
    def get_queryset(self):
        queryset = super().get_queryset()
        branch_name = self.request.query_params.get('branch_name', None)
        branch_id = self.request.query_params.get('id', None)
        
        if branch_name:
            queryset = queryset.filter(branch_name__icontains=branch_name)
        if branch_id:
            queryset = queryset.filter(id=branch_id)
            
        return queryset
    def perform_create(self, serializer):
        serializer.validated_data['added_by'] = self.request.user
        instance = serializer.save()
        if instance.bank_manager:
            instance.status = 'active'
            instance.save()
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if not queryset.exists(): 
            return Response({'message': 'No branches found.'}, status=status.HTTP_404_NOT_FOUND)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
class BranchDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance_id = instance.id
        instance.delete()
        message = f"Branch with ID {instance_id} is deleted."
        return Response({"message": message}, status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
class AccountTypePagination(PageNumberPagination):
    page_size = 3
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 100  


class AccountTypeListCreateAPIView(generics.ListCreateAPIView):
    queryset = AccountType.objects.all()
    serializer_class = AccountTypeSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = AccountTypePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['account_type', 'account_subtype','status']
    ordering_fields = ['account_type', 'account_subtype','status']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
#To add Desposit type
class DespositTypeListCreateAPIView(generics.ListCreateAPIView):
    queryset = Deposit.objects.all()
    serializer_class = DespositTypeSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = AccountTypePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['deposit_type', ]
    ordering_fields = ['deposit_type', 'account_subtype','status']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
class AccountTypeDetailsAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset=AccountType.objects.all()
    serializer_class=AccountTypeSerializer
    permission_classes=[permissions.IsAdminUser]
    pagination_class = AccountTypePagination

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance_id = instance.id
        instance.delete()
        message = f"AccountType with ID {instance_id} is deleted."
        return Response({"message": message}, status=status.HTTP_204_NO_CONTENT)
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class DepositTypeDetailsAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Deposit.objects.all()
    serializer_class = DespositTypeSerializer
    permission_classes=[permissions.IsAdminUser]
    pagination_class = AccountTypePagination

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance_id = instance.id
        instance.delete()
        message = f"DepositType with ID {instance_id} is deleted."
        return Response({"message": message}, status=status.HTTP_204_NO_CONTENT)
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
#To Customer  Desposit Creation
class DepositCreateAPIView(APIView):
    serializer_class = DepositCreationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Check if user is a customer and active
        if request.user.user_type != 'customer' or request.user.account.status != 'approved':
            return Response({"error": "Only active customers can create deposits."}, status=status.HTTP_403_FORBIDDEN)

        deposit_type_id = request.data.get('deposit_type')
        amount = request.data.get('amount')
        
        # Check if deposit type and amount are provided
        if not deposit_type_id or not amount:
            return Response({"error": "Deposit type and amount are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user has sufficient balance
        if request.user.account.account_balance < amount:
            return Response({"error": "Insufficient balance."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the Deposit object corresponding to the provided ID
        try:
            deposit_type = Deposit.objects.get(pk=deposit_type_id)
        except Deposit.DoesNotExist:
            return Response({"error": "Invalid deposit type."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Deduct amount from user's account balance
            request.user.account.account_balance -= amount
            request.user.account.save()
            send_balance_notification(request.user.account)

            # Create FD/RD
            deposit = UserDeposit.objects.create(
                user=request.user,
                deposit_type=deposit_type,  # Use the Deposit object instead of the ID
                amount=amount,
                current_value=amount,
            )
            account_number = generate_deposit_account_number()
            deposit.deposit_number = account_number
            subject = 'Deposit Withdrawal Notification'
            message = f"Dear {request.user.full_name},\n\nYour withdrawal request for  Deposit has been successfully processed.\n\nWithdrawn Amount: {amount}"
            recipient_list = [request.user.email]
            send_email(subject, message, recipient_list)
            
            subject = 'Deposit Creation Notification'
            message = f"Dear {request.user.full_name},\n\nYour Deposit has been successfully created.\n\nAmount: {amount}\nDeposit Type: {deposit_type} Deposit.\nDeposit Account No:{deposit.deposit_number}"
            recipient_list = [request.user.email]
            send_email(subject, message, recipient_list)
             # Generate FD/RD account number
            account_number = generate_deposit_account_number()
            deposit.deposit_number = account_number
            deposit.save()
            Transaction.objects.create(
                        user=request.user,
                        account=request.user.account,
                        amount=-amount,  
                        transaction_type='transfer-deposit_creation',
                        
                    
   

                        
                    )
            
            Transaction.objects.create(
                        user=request.user,
                        account=request.user.account,
                        amount=amount,  
                        transaction_type='deposit_creation',
                        
                    
   

                        
                    )

           

        return Response({"message": f"{deposit_type} created successfully."}, status=status.HTTP_201_CREATED)
    
#Deposit close
class DepositCloseAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, deposit_id):
        try:
            deposit = UserDeposit.objects.get(id=deposit_id, status='open', user=request.user)
            account = Account.objects.get(user=request.user)

            with transaction.atomic():
                # Calculate interest from creation to current time
                deposit_type = deposit.deposit_type
                current_amount = deposit.amount
                interest_rate = deposit_type.interest_rate
                creation_date = deposit.created_at.date()
                current_date = datetime.now().date()
                days_difference = (current_date - creation_date).days
                daily_interest_rate = interest_rate / 365
                interest = current_amount * daily_interest_rate * days_difference

                # Update the current value with interest
                deposit.current_value = current_amount + interest
                deposit.save()

                # Add current value to user's account balance
                account.account_balance += deposit.current_value
                account.save()

                # Set deposit status to closed
                deposit.status = 'closed'
                deposit.save()
                Transaction.objects.create(
                        user=request.user,
                        account=request.user.account,
                        amount=deposit.current_value,  
                        transaction_type='deposit_clouser',
                        
                    )
                # Send notification
                subject = 'Deposit Closed Notification'
                message = f"Dear {request.user.full_name},\n\nYour deposit closure request has been successfully processed.\n\nDeposit Amount: {deposit.current_value}"
                recipient_list = [request.user.email]
                send_email(subject, message, recipient_list)

                serializer = DepositCreationSerializer(deposit)

                return Response({"message": "Deposit closed successfully.", "data": serializer.data}, status=status.HTTP_200_OK)

        except UserDeposit.DoesNotExist:
            return Response({"error": "Deposit does not exist or is already closed."}, status=status.HTTP_404_NOT_FOUND)
        except Account.DoesNotExist:
            return Response({"error": "User account not found."}, status=status.HTTP_404_NOT_FOUND)


def generate_deposit_account_number():
    return '8080' + ''.join(str(random.randint(0, 9)) for _ in range(8))
    
class BankStaffListCreateAPIView(generics.ListCreateAPIView):
    queryset = BankStaff.objects.all()
    serializer_class = BankStaffSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = AccountTypePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['designation', 'branch']
    ordering_fields = ['designation', 'branch']
    def get_queryset(self):
        queryset = super().get_queryset()
        designation = self.request.query_params.get('designation', None)
        branch_id = self.request.query_params.get('branch_id', None)
        
        if designation:
            queryset = queryset.filter(designation__icontains=designation)
        if branch_id:
            queryset = queryset.filter(id=branch_id)
            
        return queryset
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if not queryset.exists(): 
            return Response({'message': 'No branches found.'}, status=status.HTTP_404_NOT_FOUND)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Check if the requesting user is an admin
        if not request.user.is_superuser:
            return Response({"message": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class BankStaffDetailsAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset=BankStaff.objects.all()
    serializer_class=BankStaffSerializer
    permission_classes=[permissions.IsAdminUser]
    pagination_class = AccountTypePagination

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance_id = instance.id
        instance.delete()
        message = f"BankStaff with ID {instance_id} is deleted."
        return Response({"message": message}, status=status.HTTP_204_NO_CONTENT)
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    


 # Generate a unique 15-digit account number starting with '4500'
def generate_account_number():
    return '4500' + ''.join(str(random.randint(0, 9)) for _ in range(11))
# Generate a unique 16-digit debit card number conforming to Visa standards
def generate_debit_card_number():
    return '4' + ''.join(str(random.randint(0, 9)) for _ in range(15))
class AccountCreateAPIView(APIView):
    serializer_class = AccountCreationSerializer

    def post(self, request, *args, **kwargs):
       
        if Account.objects.filter(user=request.user).exists():
            return Response({"error": "User already has an account."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['user'] = request.user
            
            serializer.save()
            subject = 'Account Creation Notification'
            message = f"Your bank account opening application has been submitted."
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [request.user.email]
            send_mail(subject, message, email_from, recipient_list)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AccountApprovalAPIView(APIView):
    def put(self, request, account_id, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 'staff':
            staff = BankStaff.objects.get(user=request.user)
            if staff.designation == 'manager' and staff.branch.bank_manager == request.user:
                action = request.data.get('action')  # Assuming the action (approve/reject) is sent in the request data
                account = Account.objects.get(id=account_id)
                
                if account.status == 'applied':  
                    if action == 'approve':
                        account.status = 'approved'
                        account.account_number = generate_account_number() 
                        account.debit_card_number = generate_debit_card_number() 
                        account.save()
                        minimum_balance_message = "To activate your account, you need to deposit the minimum balance required. Once the minimum balance is deposited, your account will be activated."

                        # Send email to user
                        subject = 'Account Approval Notification'
                        message = f"Your account has been approved.\n\nAccount details:\nName: {account.user.full_name}\nAccount number: {account.account_number}\nIFSC code: {account.branch.ifsc_code}\nBranch name: {account.branch.branch_name}\nAccount type: {account.account_variant.account_subtype}\nMinimum balance: {account.account_variant.minimum_balance}\nCharge details: Yearly debit fee: {account.account_variant.debit_card_yearly_fee}, ATM withdrawal charge after the free limit: {account.account_variant.additional_atm_charge}, Maximum withdrawal per month: {account.account_variant.monthly_transaction_limit}\n\n{minimum_balance_message}"
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = [account.user.email]
                        send_mail(subject, message, email_from, recipient_list)
                        
                        return Response({'message': 'Account approved successfully'}, status=status.HTTP_200_OK)
                    elif action == 'reject':
                        account.status = 'rejected'
                        account.save()
                        # Send email to user
                        subject = 'Account Rejection Notification'
                        message = f"Your account creation request has been rejected."
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = [account.user.email]
                        send_mail(subject, message, email_from, recipient_list)
                        
                        return Response({'message': 'Account rejected successfully'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'message': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'message': 'Only accounts with status:applied can be approved or rejected'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'Unauthorized to perform action'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'message': 'Unauthorized to perform action'}, status=status.HTTP_403_FORBIDDEN)

class AccountDetailsAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountCreationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user == instance.user or request.user.staff.branch == instance.branch:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            return Response({"message": "Unauthorized to view this account details"}, status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.staff and request.user.staff.branch == instance.branch:
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({"message": "Unauthorized to perform patch operation on this account"}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.is_authenticated and request.user.staff and request.user.staff.designation == 'manager':
            instance.delete()
            return Response({"message": f"Account with ID {instance.id} is deleted."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "Unauthorized to perform delete operation on this account"}, status=status.HTTP_403_FORBIDDEN)