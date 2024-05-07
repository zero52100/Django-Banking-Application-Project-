from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import LoanType,LoanApplication
from .serializers import  LoanTypeSerializer,LoanApplicationSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from rest_framework.views import APIView
from utilities.notifications import send_email


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
