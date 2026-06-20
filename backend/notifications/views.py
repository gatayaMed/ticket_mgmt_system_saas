from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Notification, NotificationPreference
from .serializers import NotificationSerializer, NotificationPreferenceSerializer


class NotificationListView(generics.ListAPIView):
    """List user's notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).order_by('-created_at')


class NotificationUnreadCountView(generics.GenericAPIView):
    """Get unread notification count"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return Response({'unread_count': count})


class NotificationMarkReadView(generics.GenericAPIView):
    """Mark notification(s) as read"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        notification_ids = request.data.get('notification_ids', [])
        if notification_ids:
            Notification.objects.filter(
                id__in=notification_ids,
                user=request.user
            ).update(is_read=True, read_at=timezone.now())
        else:
            Notification.objects.filter(
                user=request.user,
                is_read=False
            ).update(is_read=True, read_at=timezone.now())

        return Response({'status': 'success'})


class NotificationPreferencesView(generics.RetrieveUpdateAPIView):
    """Get or update notification preferences"""
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        pref, _ = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return pref
