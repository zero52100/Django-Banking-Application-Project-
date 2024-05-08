from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import SavingsGoal,Budget, Expense
from .serializers import SavingsGoalSerializer,BudgetSerializer, ExpenseSerializer
from accounts.models import Account
from utilities.pagination import  CustomPagination
from utilities.notifications import send_email


from rest_framework.exceptions import NotFound

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
class BudgetCreateAPIView(generics.CreateAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        # Check if the user already has a budget
        if Budget.objects.filter(user=user).exists():
            return Response({'error': 'A budget already exists for this user.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if user.user_type == 'customer' and user.account.status == 'approved':
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            
            remaining_budget = serializer.validated_data.get('monthly_budget')
            serializer.validated_data['remaining_budget'] = remaining_budget
            
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

            
        else:
            return Response({'error': 'You are not eligible to create a budget.'}, status=status.HTTP_403_FORBIDDEN)
        
class BudgetListAPIView(generics.ListAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return Budget.objects.filter(user=user)
    
class ExpenseListAPIView(generics.ListAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return Budget.objects.filter(user=user)

class ExpenseCreateAPIView(generics.CreateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        if user.user_type == 'customer' and user.account.status == 'approved':
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)

            # Update remaining budget
            budget = Budget.objects.get(user=user)
            budget.remaining_budget -= serializer.validated_data['amount']
            budget.save()

            # Send email notification if remaining budget is negative
            if budget.remaining_budget < 0:
                send_email(
                    'Budget Exceeded',
                    f'You have exceeded your monthly budget. Remaining budget: {budget.remaining_budget}',
                    [user.email],
                )
                

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'You are not eligible to create an expense.'}, status=status.HTTP_403_FORBIDDEN)



class BudgetDetailsAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return Budget.objects.filter(user=user)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance_id = instance.id
        instance.delete()
        message = f"Budget with ID {instance_id} is deleted."
        return Response({"message": message}, status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user.user_type != 'customer':
            return Response({"error": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user.user_type != 'customer':
            return Response({"error": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class ExpenseDetailsAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return Expense.objects.filter(user=user)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance_id = instance.id
        instance.delete()
        message = f"Expense with ID {instance_id} is deleted."
        return Response({"message": message}, status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user.user_type != 'customer':
            return Response({"error": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user.user_type != 'customer':
            return Response({"error": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
