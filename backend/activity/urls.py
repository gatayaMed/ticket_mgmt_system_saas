from django.urls import path
from .views import ActivityFeedView, EntityActivityView

urlpatterns = [
    path('feed/', ActivityFeedView.as_view(), name='activity-feed'),
    path('entity/<str:content_type>/<int:object_id>/', EntityActivityView.as_view(), name='entity-activity'),
]
