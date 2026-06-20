from django.contrib import admin
from .models import (
    DeveloperProfile, AIAssignmentSuggestion,
    AssignmentHistory, AICache, AIMetrics
)


@admin.register(DeveloperProfile)
class DeveloperProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'years_experience', 'current_workload', 'success_rate', 'is_available']
    list_filter = ['is_available']
    search_fields = ['user__username']


@admin.register(AIAssignmentSuggestion)
class AIAssignmentSuggestionAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'status', 'manager_approved_choice', 'created_at']
    list_filter = ['status']
    search_fields = ['ticket__ticket_id']


@admin.register(AssignmentHistory)
class AssignmentHistoryAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'assigned_by', 'assigned_to', 'was_ai_suggestion', 'created_at']
    list_filter = ['was_ai_suggestion', 'manager_approved']


@admin.register(AIMetrics)
class AIMetricsAdmin(admin.ModelAdmin):
    list_display = ['provider', 'endpoint', 'success', 'request_time', 'tokens_used', 'created_at']
    list_filter = ['provider', 'success']
