from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    mobile_number = serializers.CharField(max_length=10, validators=[RegexValidator(regex=r'^\d{10}$', message='Mobile number must be exactly 10 digits')])
    user_type = serializers.ChoiceField(choices=User.USER_TYPES, default='customer')

    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'mobile_number', 'date_of_birth', 'password', 'password2', 'user_type','otp')

    def validate(self, data):
        
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        
        
        validate_password(data['password'])
        if User.objects.filter(mobile_number=data['mobile_number']).exists():
            raise serializers.ValidationError("Mobile number is already in use.")
        
        return data
        

    def create(self, validated_data):
        
        validated_data.pop('password2')
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyOTPAndResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(max_length=128)
    confirm_password = serializers.CharField(max_length=128)