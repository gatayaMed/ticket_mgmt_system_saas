from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/organizations/', include('organizations.urls')),
    path('api/', include('projects.urls')), 
    path('api/', include('tickets.urls')),
    path('api/', include('comments.urls')), 
    path('api/', include('attachments.urls')),
    # Notifications
    path('api/notifications/', include('notifications.urls')),
    # Dashboard
    path('api/dashboard/', include('dashboard.urls')),
    # Sprints
    path('api/sprints/', include('sprints.urls')),
    # Reports
    path('api/reports/', include('reports.urls')),
    # Webhooks
    path('api/webhooks/', include('webhooks.urls')),
    # Search
    path('api/search/', include('search.urls')),
    # Activity
    path('api/activity/', include('activity.urls')),
    # AI Integration
    path('api/ai/', include('ai.urls')),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)