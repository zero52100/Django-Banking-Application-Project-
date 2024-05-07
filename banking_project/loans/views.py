from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import LoanType
from .serializers import  LoanTypeSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from rest_framework.views import APIView
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
