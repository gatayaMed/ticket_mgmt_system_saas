from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import AttachmentListCreateView, AttachmentDetailView

urlpatterns = [
    path('tickets/<int:ticket_id>/attachments/',
         AttachmentListCreateView.as_view(),
         name='attachment-list-create'),
    
    path('attachments/<int:pk>/',
         AttachmentDetailView.as_view(),
         name='attachment-detail'),
]# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)