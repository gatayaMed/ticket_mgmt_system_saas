from django.contrib import admin
from .models import Organization, Membership, Invitation

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_by', 'created_at', 'is_active']
    search_fields = ['name', 'slug', 'description']
    list_filter = ['is_active', 'created_at']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'role', 'is_active', 'joined_at']
    search_fields = ['user__email', 'organization__name']
    list_filter = ['role', 'is_active', 'organization']

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ['email', 'organization', 'role', 'status', 'invited_by', 'created_at']
    search_fields = ['email', 'organization__name']
    list_filter = ['status', 'role', 'organization']