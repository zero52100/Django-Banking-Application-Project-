from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import LoanType,LoanApplication
from transactions.models import Transaction
from accounts.models import Account, BankStaff
from django.db import transaction
from django.core.exceptions import PermissionDenied
from .serializers import  LoanTypeSerializer,LoanApplicationSerializer,LoanApprovalSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from rest_framework.views import APIView
from utilities.notifications import send_email
from datetime import datetime
from django.conf import settings



import random


class CustomPagination(PageNumberPagination):
    page_size = 3
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 100
class LoanTypeListCreateView(generics.ListCreateAPIView):
    queryset = LoanType.objects.all()
    serializer_class = LoanTypeSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name' ]
    ordering_fields = ['name']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
class LoanTypeDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LoanType.objects.all()
    serializer_class = LoanTypeSerializer
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoanApplicationCreateView(generics.CreateAPIView):
    serializer_class = LoanApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user

        # Check if the user is a customer and their account is approved
        if user.user_type == 'customer' and user.account.status == 'approved':
            loan_type_id = int(request.data.get('loan_type'))  # Convert to integer
            amount = request.data.get('amount')

            # Check if the loan type exists
            loan_type = LoanType.objects.filter(id=loan_type_id).first()
            if loan_type:
                # Add debug logging
               
                
                # Check if the loan amount is within the range of min and max loan amounts
                if loan_type.min_loan_amount <= amount <= loan_type.max_loan_amount:
                    # Create a new loan application
                    loan_application = LoanApplication.objects.create(
                        user=user,
                        loan_type=loan_type,
                        amount=amount,
                        status='applied',
                        
                        branch_id=user.account.branch_id,
                        outstanding_balance=0
                    )
                    subject = 'Loan Application Notification'
                    message = f"Your {loan_type.name} Loan application has been submitted."
                    recipient_list = [user.email]
                    send_email(subject, message, recipient_list)

                    serializer = self.get_serializer(loan_application)
                    
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response({'error': 'Loan amount must be between min and max loan amounts'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Invalid loan type'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'User must be a customer with an approved account'}, status=status.HTTP_400_BAD_REQUEST)
 # Generate a unique 15-digit  loan account number starting with '4500'
def generate_loan_account_number():
    return '3300' + ''.join(str(random.randint(0, 9)) for _ in range(11))
class LoanApprovalAPIView(generics.GenericAPIView):
    serializer_class = LoanApprovalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        staff = BankStaff.objects.filter(user=user, designation='loan_officer').first()
        # Check if the user is a loan officer
        if staff:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            action = serializer.validated_data['action']
            loan_application_id = serializer.validated_data['loan_application_id']

            try:
                loan_application = LoanApplication.objects.get(id=loan_application_id)
                print("Loan application status:", loan_application.user)  # Moved print statement here
            except LoanApplication.DoesNotExist:
                return Response({'error': 'Loan application not found'}, status=status.HTTP_404_NOT_FOUND)

            print("Staff branch ID:", staff.branch_id)
            print("Loan application branch ID:", loan_application.branch_id)
            print("Loan application status:", loan_application.status)
            
            # Check if the loan application belongs to the same branch as the loan officer
            if loan_application.branch_id != staff.branch_id:
                raise PermissionDenied("You don't have permission to process this loan application.")
            
            # Check if the loan application is already approved or closed
            if loan_application.status in ['approved', 'closed']:
                return Response({'error': 'Loan application is already approved or closed'}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                if action == 'approve':
                    # Update loan status to approved
                    loan_application.status = 'approved'
                    loan_application.save()
                    loan_application.loan_account_number = generate_loan_account_number() 
                    
                    # Transfer loan amount to user's bank account and update balance
                    loan_application.user.account.account_balance += loan_application.amount
                    loan_application.user.account.save()
                    processing_fee_transaction = Transaction.objects.create(
                        user=loan_application.user,
                        account=loan_application.user.account,
                        amount=loan_application.amount,  
                        transaction_type='loan_sactioned',
                        destination_account_number=loan_application.loan_account_number,
                    
   

                        
                    )
                    subject = 'Loan Sanctioned Notification'
                    message = f"Your {loan_application.loan_type.name} loan application has been sanctioned. The amount has been transferred to account number: {loan_application.user.account.account_number}.\nLoan account number: {loan_application.loan_account_number}\nSanctioned amount: {loan_application.amount}"
                    recipient_list = [loan_application.user.email]
                    send_email(subject, message, recipient_list)
                    processing_fee_transaction.account_balance = loan_application.user.account.account_balance
                    processing_fee_transaction.save()

                    # Calculate and update outstanding balance with interest
                    current_date = datetime.now().date()
                    creation_date = loan_application.created_at.date()
                    months_since_creation = (current_date.year - creation_date.year) * 12 + current_date.month - creation_date.month
                    interest_rate_per_month = loan_application.loan_type.interest_rate / 100 / 12
                    outstanding_balance = loan_application.amount * ((1 + interest_rate_per_month) ** months_since_creation)
                    loan_application.outstanding_balance = outstanding_balance
                    loan_application.save()

                    # If outstanding balance is fully paid, update status to closed
                    if loan_application.outstanding_balance <= 0:
                        loan_application.status = 'closed'
                        loan_application.save()

                    # Create a transaction for processing fee deduction
                    processing_fee_transaction = Transaction.objects.create(
                        user=loan_application.user,
                        account=loan_application.user.account,
                        amount=-loan_application.loan_type.processing_fee,  
                        transaction_type='processing_fee',
                        

                        
                    )
                    processing_fee_transaction.account_balance = loan_application.user.account.account_balance - processing_fee_transaction.amount
                    processing_fee_transaction.save()

                    return Response({'message': 'Loan application approved successfully'}, status=status.HTTP_200_OK)

                elif action == 'reject':
                   
                    loan_application.status = 'rejected'
                    loan_application.save()

                    subject = 'Loan Rejection Notification'
                    message = f"Your {loan_application.loan_type.name} loan application has been rejected. Please contact us for further details."
                    recipient_list = [loan_application.user.email]
                    send_email(subject, message, recipient_list)

                    return Response({'message': 'Loan application rejected successfully'}, status=status.HTTP_200_OK)

                else:
                    return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise PermissionDenied("You don't have permission to process loans.")