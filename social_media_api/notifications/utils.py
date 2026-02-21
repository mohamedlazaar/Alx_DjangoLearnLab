from django.contrib.contenttypes.models import ContentType

from .models import Notification


def create_notification(recipient, verb, actor=None, target=None):
    """
    Create a notification for an action.
    recipient: User who receives the notification.
    verb: Short description, e.g. "followed you", "liked your post", "commented on your post".
    actor: User who performed the action (optional).
    target: Optional object (Post, Comment, etc.) for GenericForeignKey.
    """
    content_type = None
    object_id = None
    if target is not None:
        content_type = ContentType.objects.get_for_model(target)
        object_id = target.pk
    return Notification.objects.create(
        recipient=recipient,
        actor=actor,
        verb=verb,
        content_type=content_type,
        object_id=object_id,
    )
