# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import User

class CustomUserAdmin(UserAdmin):
    """
    Custom admin configuration for the User model.
    Extends Django's default UserAdmin to work with custom User model.
    """
    
    # These are the fields that will be displayed in the list view
    list_display = ('id', 'username', 'email', 'phone', 'is_active', 'is_staff', 'created_at')
    
    # These are the fields that will be used for filtering
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'created_at')
    
    # These are the fields that will be searchable
    search_fields = ('username', 'email', 'phone', 'first_name', 'last_name')
    
    # These fields will be read-only in the detail view
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')
    
    # This is the layout for the detail/edit view
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    
    # This is the layout for the "Add User" view
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )
    
    # Default ordering
    ordering = ('-created_at',)

# Register your custom User model
admin.site.register(User, CustomUserAdmin)

# Optional: Unregister the Group model if you don't need it
# admin.site.unregister(Group)