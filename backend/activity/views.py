from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from .models import Activity, ActivityFeed
from organizations.models import Organization


class ActivityFeedView(generics.GenericAPIView):
    """Get activity feed for the current user"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))
        activities = ActivityFeed.get_feed(request.user, limit=limit, offset=offset)

        data = [{
            'id': a.id,
            'user': a.user.username,
            'action': a.action,
            'action_display': a.get_action_display(),
            'description': a.description,
            'content_type': a.content_type.model if a.content_type else None,
            'object_id': a.object_id,
            'metadata': a.metadata,
            'created_at': a.created_at.isoformat()
        } for a in activities]

        return Response({
            'count': len(data),
            'results': data
        })


class EntityActivityView(generics.GenericAPIView):
    """Get activity for a specific entity (ticket, project, etc.)"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, content_type, object_id):
        try:
            ct = ContentType.objects.get(model=content_type)
            limit = int(request.query_params.get('limit', 50))
            activities = Activity.objects.filter(
                content_type=ct,
                object_id=object_id
            ).select_related('user')[:limit]

            data = [{
                'id': a.id,
                'user': a.user.username,
                'action': a.action,
                'action_display': a.get_action_display(),
                'description': a.description,
                'metadata': a.metadata,
                'created_at': a.created_at.isoformat()
            } for a in activities]

            return Response({
                'count': len(data),
                'results': data
            })
        except ContentType.DoesNotExist:
            return Response(
                {'error': 'Invalid content type'},
                status=status.HTTP_400_BAD_REQUEST
            )
