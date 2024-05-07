

from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'mobile_number', 'date_of_birth', 'user_type', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_active', 'date_joined')
    search_fields = ('email', 'full_name', 'mobile_number')


admin.site.register(User, UserAdmin)
