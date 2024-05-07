import random
from django.core.mail import send_mail
from rest_framework import generics, status
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import LoginSerializer
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def generate_otp(self):
        return str(random.randint(100000, 999999))

    def send_otp_email(self, email, otp):
        subject = 'OTP for User Registration'
        message = f'Your OTP for user registration is: {otp}'
        from_email = 'your_email@gmail.com' 
        send_mail(subject, message, from_email, [email])

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp = self.generate_otp()
        self.send_otp_email(email, otp)

        user_type = request.data.get('user_type', 'customer')
        if user_type not in ['staff', 'admin', 'customer']:
            return Response({'message': 'Invalid user type.'}, status=status.HTTP_400_BAD_REQUEST)

        if user_type == 'admin':
            if not self.request.user.is_superuser:
                return Response({'message': 'Only superusers can create admin users.'}, status=status.HTTP_403_FORBIDDEN)
        serializer.save(user_type=user_type, otp=otp)
        return Response({'message': 'An OTP has been sent to your email for verification.'}, status=status.HTTP_201_CREATED)
    
class VerifyOTPView(generics.GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        otp = request.data.get('otp')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        print("Stored OTP:", user.otp) 
        print("Entered OTP:", otp)  
        if user.is_active:
            return Response({'message': 'User is already active.'}, status=status.HTTP_400_BAD_REQUEST)

        if otp == user.otp:
            user.is_active = True
            user.otp=None
            user.save()
            return Response({'message': 'User account activated successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # Retrieve the user based on the email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'message': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

            
            if not user.is_active:
                return Response({'message': 'User account is not active.'}, status=status.HTTP_401_UNAUTHORIZED)

            
            if not user.check_password(password):
                return Response({'message': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Login successful.',
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)