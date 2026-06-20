from django.urls import path
from .views import CommentListCreateView, CommentDetailView

urlpatterns = [
    path('tickets/<int:ticket_id>/comments/',
         CommentListCreateView.as_view(),
         name='comment-list-create'),
    
    path('comments/<int:pk>/',
         CommentDetailView.as_view(),
         name='comment-detail'),
]