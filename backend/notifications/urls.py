from django.urls import path
from .views import (
    NotificationListView, NotificationUnreadCountView,
    NotificationMarkReadView, NotificationPreferencesView
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('unread-count/', NotificationUnreadCountView.as_view(), name='notification-unread-count'),
    path('mark-read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('preferences/', NotificationPreferencesView.as_view(), name='notification-preferences'),
]
