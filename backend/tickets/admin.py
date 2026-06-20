# tickets/admin.py
from django.contrib import admin
from .models import Ticket, TicketHistory

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_id', 'title', 'project', 'status', 'priority', 'assignee', 'created_at']
    list_filter = ['status', 'priority', 'ticket_type', 'project']
    search_fields = ['ticket_id', 'title', 'description']
    readonly_fields = ['ticket_id', 'created_at', 'updated_at', 'completed_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('ticket_id', 'title', 'description', 'project', 'organization')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'ticket_type')
        }),
        ('Assignment', {
            'fields': ('assignee', 'created_by')
        }),
        ('Dates', {
            'fields': ('due_date', 'estimated_hours', 'completed_at')
        }),
        ('Metadata', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

@admin.register(TicketHistory)
class TicketHistoryAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'action', 'user', 'created_at']
    list_filter = ['action']
    search_fields = ['ticket__ticket_id', 'description']
    readonly_fields = ['created_at']