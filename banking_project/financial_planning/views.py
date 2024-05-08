from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import SavingsGoal
from .serializers import SavingsGoalSerializer
from accounts.models import Account

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
