from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
# Register your models here.


class UserAdmin(BaseUserAdmin):
    ordering = ['created_at']
    # listフィールド用のフィールドセット
    list_display = ['first_name', 'last_name',
                    'username', 'phone_number', 'email', 'is_active']
    # フィールドセットを使用することでadmin表示分割する
    # edit用のフィールドセット
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            ('Personal Info'),
            {'fields': ('first_name', 'last_name',
                        'username', 'phone_number',)}),
        (
            ('Permissions'),
            {'fields': ('is_admin', 'is_active',
                        'is_staff', 'is_superuser',)}),
    )
    # 追加用のフィールドセット
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'email', 'password1', 'password2',)
        }),
    )


admin.site.register(User, UserAdmin)
