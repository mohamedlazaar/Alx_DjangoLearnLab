"""
Tests for notifications: list, unread filter, mark read, and creation on follow/like/comment.
Run: python manage.py test notifications
"""
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from notifications.models import Notification
from posts.models import Post

User = get_user_model()


class NotificationAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="pass123")
        self.actor = User.objects.create_user(username="actor", password="pass123")

    def test_list_notifications_requires_auth(self):
        response = self.client.get("/api/notifications/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_notifications_empty(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/notifications/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 0)

    def test_list_notifications_shows_own_only(self):
        Notification.objects.create(
            recipient=self.user, actor=self.actor, verb="followed you"
        )
        other_user = User.objects.create_user(username="other", password="pass123")
        Notification.objects.create(
            recipient=other_user, actor=self.actor, verb="followed you"
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/notifications/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["verb"], "followed you")
        self.assertEqual(response.data["results"][0]["actor_username"], "actor")

    def test_list_notifications_unread_only(self):
        n1 = Notification.objects.create(
            recipient=self.user, actor=self.actor, verb="followed you", is_read=False
        )
        n2 = Notification.objects.create(
            recipient=self.user, actor=self.actor, verb="liked your post", is_read=True
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/notifications/?unread_only=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], n1.id)

    def test_mark_single_notification_read(self):
        n = Notification.objects.create(
            recipient=self.user, actor=self.actor, verb="followed you", is_read=False
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f"/api/notifications/{n.pk}/read/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        n.refresh_from_db()
        self.assertTrue(n.is_read)
        self.assertIsNotNone(n.read_at)

    def test_mark_all_notifications_read(self):
        Notification.objects.create(
            recipient=self.user, actor=self.actor, verb="followed you", is_read=False
        )
        Notification.objects.create(
            recipient=self.user, actor=self.actor, verb="liked your post", is_read=False
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/notifications/read-all/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Notification.objects.filter(recipient=self.user, is_read=False).count(), 0
        )

    def test_notification_created_on_follow(self):
        self.client.force_authenticate(user=self.actor)
        response = self.client.post(f"/api/accounts/follow/{self.user.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.user, actor=self.actor, verb="followed you"
            ).exists()
        )

    def test_notification_created_on_comment(self):
        post = Post.objects.create(
            author=self.user, title="Post", content="Content"
        )
        self.client.force_authenticate(user=self.actor)
        response = self.client.post(
            "/api/comments/",
            {"post": post.pk, "content": "A comment"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.user,
                actor=self.actor,
                verb="commented on your post",
            ).exists()
        )