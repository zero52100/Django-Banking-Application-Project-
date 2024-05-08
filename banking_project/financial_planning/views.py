from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import SavingsGoal
from .serializers import SavingsGoalSerializer
from accounts.models import Account
from utilities.pagination import  CustomPagination

class SavingsGoalCreateAPIView(generics.CreateAPIView):
    serializer_class = SavingsGoalSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        if user.user_type == 'customer' and user.account.status == 'approved':
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'You are not eligible to create a savings goal.'}, status=status.HTTP_403_FORBIDDEN)
class SavingsGoalListAPIView(generics.ListAPIView):
    serializer_class = SavingsGoalSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return SavingsGoal.objects.filter(user=user)


class SavingsGoalDetailsAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SavingsGoalSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return SavingsGoal.objects.filter(user=user)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance_id = instance.id
        instance.delete()
        message = f"Savings goal with ID {instance_id} is deleted."
        return Response({"message": message}, status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != 'processing':
            return Response({"error": "You can only edit savings goals with status 'processing'."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != 'processing':
            return Response({"error": "You can only edit savings goals with status 'processing'."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)