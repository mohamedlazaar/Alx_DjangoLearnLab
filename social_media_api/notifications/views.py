from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(ListAPIView):
    """
    List notifications for the authenticated user.
    Unread notifications can be shown first via query param ?unread_only=1.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Notification.objects.filter(recipient=self.request.user).select_related(
            "actor"
        )
        if self.request.query_params.get("unread_only") == "1":
            qs = qs.filter(is_read=False)
        return qs


class NotificationMarkReadView(APIView):
    """Mark a single notification as read, or mark all as read."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk=None):
        if pk is not None:
            notification = Notification.objects.filter(
                recipient=request.user, pk=pk
            ).first()
            if not notification:
                return Response(
                    {"detail": "Not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
            return Response({"detail": "Notification marked as read."})
        # Mark all as read
        updated = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).update(is_read=True, read_at=timezone.now())
        return Response({"detail": f"Marked {updated} notification(s) as read."})
