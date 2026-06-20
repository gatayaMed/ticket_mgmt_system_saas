# comments/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Comment model
    """
    
    # List view configuration
    list_display = [
        'id',
        'ticket_link',
        'user_link',
        'content_preview',
        'is_edited',
        'is_active',
        'created_at',
        'updated_at'
    ]
    
    list_display_links = ['id', 'ticket_link', 'user_link']
    
    list_filter = [
        'is_edited',
        'is_active',
        'created_at',
        'user',
        'ticket'
    ]
    
    search_fields = [
        'content',
        'user__username',
        'user__email',
        'ticket__title',
        'ticket__ticket_id'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'ticket_link',
        'user_link',
        'content_full'
    ]
    
    fieldsets = (
        ('Comment Information', {
            'fields': (
                'ticket',
                'user',
                'content',
                'is_edited',
                'is_active'
            )
        }),
        ('Preview', {
            'fields': ('content_full',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at',
                'ticket_link',
                'user_link'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'mark_as_edited',
        'mark_as_not_edited',
        'activate_comments',
        'deactivate_comments'
    ]
    
    # Date hierarchy
    date_hierarchy = 'created_at'
    
    # Default ordering
    ordering = ['-created_at']
    
    # Number of items per page
    list_per_page = 50
    
    def ticket_link(self, obj):
        """Link to the ticket in admin"""
        url = reverse('admin:tickets_ticket_change', args=[obj.ticket.id])
        return format_html(
            '<a href="{}">{} - {}</a>',
            url,
            obj.ticket.ticket_id,
            obj.ticket.title[:30]
        )
    ticket_link.short_description = 'Ticket'
    ticket_link.admin_order_field = 'ticket__ticket_id'
    
    def user_link(self, obj):
        """Link to the user in admin"""
        url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.user.email
        )
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__email'
    
    def content_preview(self, obj):
        """Preview of comment content"""
        if len(obj.content) > 50:
            return f"{obj.content[:50]}..."
        return obj.content
    content_preview.short_description = 'Content Preview'
    
    def content_full(self, obj):
        """Full comment content with formatting"""
        return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 4px; '
            'white-space: pre-wrap; max-height: 300px; overflow: auto;">{}</div>',
            obj.content
        )
    content_full.short_description = 'Full Content'
    
    # Bulk actions
    def mark_as_edited(self, request, queryset):
        """Mark selected comments as edited"""
        updated = queryset.update(is_edited=True)
        self.message_user(request, f'{updated} comments marked as edited.')
    mark_as_edited.short_description = 'Mark selected comments as edited'
    
    def mark_as_not_edited(self, request, queryset):
        """Mark selected comments as not edited"""
        updated = queryset.update(is_edited=False)
        self.message_user(request, f'{updated} comments marked as not edited.')
    mark_as_not_edited.short_description = 'Mark selected comments as not edited'
    
    def activate_comments(self, request, queryset):
        """Activate selected comments"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} comments activated.')
    activate_comments.short_description = 'Activate selected comments'
    
    def deactivate_comments(self, request, queryset):
        """Deactivate selected comments"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} comments deactivated.')
    deactivate_comments.short_description = 'Deactivate selected comments'

    # Inline admin for comments on Ticket admin
    def get_actions(self, request):
        """Customize actions based on user permissions"""
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            actions.pop('delete_selected', None)
        return actions


class CommentInline(admin.TabularInline):
    """
    Inline admin for displaying comments on Ticket admin page
    """
    model = Comment
    extra = 0
    fields = [
        'user',
        'content_preview',
        'is_edited',
        'created_at'
    ]
    readonly_fields = [
        'user',
        'content_preview',
        'is_edited',
        'created_at'
    ]
    can_delete = True
    show_change_link = True
    max_num = None
    
    def content_preview(self, obj):
        """Preview of content"""
        if len(obj.content) > 100:
            return f"{obj.content[:100]}..."
        return obj.content
    content_preview.short_description = 'Content'
    
    def has_add_permission(self, request, obj=None):
        """Disable add in inline"""
        return False


# Optional: Register with Ticket admin
# Uncomment this if you want to show comments inline in Ticket admin
# from tickets.admin import TicketAdmin
# TicketAdmin.inlines = getattr(TicketAdmin, 'inlines', []) + [CommentInline]