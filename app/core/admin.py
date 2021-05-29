from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
# Register your models here.


class UserAdmin(BaseUserAdmin):
    ordering = ['created_at']
    list_display = ['first_name', 'last_name',
                    'username', 'phone_number', 'email']


admin.site.register(User, UserAdmin)
