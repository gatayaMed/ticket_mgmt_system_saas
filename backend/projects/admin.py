# projects/admin.py
from django.contrib import admin
from .models import Project, ProjectMember

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'status', 'priority', 'created_by', 'created_at']
    list_filter = ['status', 'priority', 'organization', 'is_active']
    search_fields = ['name', 'description', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'slug', 'organization')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'progress')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'due_date')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at', 'is_active')
        }),
    )

@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ['project', 'user', 'role', 'joined_at', 'is_active']
    list_filter = ['role', 'is_active', 'project']
    search_fields = ['user__email', 'project__name']