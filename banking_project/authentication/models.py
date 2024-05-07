from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from datetime import datetime
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, full_name, mobile_number, date_of_birth, user_type='customer', password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
            mobile_number=mobile_number,
            date_of_birth=date_of_birth,
            user_type=user_type,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staff(self, email, full_name, mobile_number, date_of_birth, password=None):
        return self.create_user(
            email=email,
            full_name=full_name,
            mobile_number=mobile_number,
            date_of_birth=date_of_birth,
            user_type='staff',
            password=password,
        )

    def create_superuser(self, email, full_name, mobile_number, date_of_birth, password=None):
        user = self.create_user(
            email=email,
            full_name=full_name,
            mobile_number=mobile_number,
            date_of_birth=date_of_birth,
            user_type='admin',
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user
    
    def has_module_perms(self, user_obj, app_label):
        return user_obj.is_staff or user_obj.is_superuser


class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPES = [
        ('staff', 'Staff'),
        ('admin', 'Admin'),
        ('customer', 'Customer'),
    ]

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=10, unique=True)
    date_of_birth = models.DateField()
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='customer')
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_superuser = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True) 
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'mobile_number', 'date_of_birth']

    def save(self, *args, **kwargs):
        if self.date_of_birth:
            today = timezone.now().date()
            age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            self.age = age
    
        super().save(*args, **kwargs)
