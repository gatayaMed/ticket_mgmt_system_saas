from django.urls import path
from . import views

urlpatterns = [
    # Ticket Classification
    path('classify/', views.classify_ticket, name='ai-classify'),

    # Priority Prediction
    path('predict-priority/', views.predict_priority, name='ai-predict-priority'),

    # Smart Assignment (Manager Approval)
    path('suggest-assignee/<int:ticket_id>/', views.suggest_assignee, name='ai-suggest-assignee'),
    path('approve-suggestion/', views.approve_suggestion, name='ai-approve-suggestion'),
    path('reject-suggestion/', views.reject_suggestion, name='ai-reject-suggestion'),
    path('tickets/unassigned/', views.unassigned_tickets, name='ai-unassigned-tickets'),
    path('assignment-stats/', views.assignment_stats, name='ai-assignment-stats'),

    # Chatbot
    path('chat/', views.chat, name='ai-chat'),

    # Sentiment
    path('sentiment/<int:ticket_id>/', views.analyze_sentiment, name='ai-sentiment'),

    # Similar Tickets
    path('similar-tickets/<int:ticket_id>/', views.similar_tickets, name='ai-similar-tickets'),

    # Response Generation
    path('generate-response/<int:ticket_id>/', views.generate_response, name='ai-generate-response'),

    # Enhanced Search
    path('enhance-search/', views.enhance_search, name='ai-enhance-search'),

    # Metrics & Profiles
    path('metrics/', views.ai_metrics, name='ai-metrics'),
    path('developer-profiles/', views.developer_profiles, name='ai-developer-profiles'),
]
