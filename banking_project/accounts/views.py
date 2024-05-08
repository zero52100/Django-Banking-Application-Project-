from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Account, AccountType, Branch, BankStaff,Deposit
from .serializers import BranchSerializer,AccountTypeSerializer,BankStaffSerializer,AccountCreationSerializer,DespositTypeSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from rest_framework.views import APIView
import random
from django.core.mail import send_mail
from django.conf import settings

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