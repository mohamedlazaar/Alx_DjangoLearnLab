"""
Basic API tests for posts, comments, and likes.
Run: python manage.py test posts
"""
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Comment, Like, Post

User = get_user_model()


class PostAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.post = Post.objects.create(author=self.user, title="Test Post", content="Content")

    def test_list_posts_unauthenticated(self):
        response = self.client.get("/api/posts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_create_post_requires_auth(self):
        response = self.client.post(
            "/api/posts/",
            {"title": "New", "content": "Body"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_post_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/posts/",
            {"title": "New Post", "content": "Body"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)

    def test_only_owner_can_delete_post(self):
        other = User.objects.create_user(username="other", password="otherpass")
        self.client.force_authenticate(user=other)
        response = self.client.delete(f"/api/posts/{self.post.pk}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/api/posts/{self.post.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CommentAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.post = Post.objects.create(author=self.user, title="Test", content="Content")
        self.comment = Comment.objects.create(post=self.post, user=self.user, content="A comment")

    def test_list_comments_filter_by_post(self):
        response = self.client.get(f"/api/comments/?post={self.post.pk}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_create_comment_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/comments/",
            {"post": self.post.pk, "content": "New comment"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.filter(post=self.post).count(), 2)

    def test_only_owner_can_delete_comment(self):
        other = User.objects.create_user(username="other", password="otherpass")
        self.client.force_authenticate(user=other)
        response = self.client.delete(f"/api/comments/{self.comment.pk}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class LikeAPITests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="pass123")
        self.liker = User.objects.create_user(username="liker", password="pass123")
        self.post = Post.objects.create(
            author=self.author, title="Post", content="Content"
        )

    def test_like_requires_auth(self):
        response = self.client.post(f"/api/posts/{self.post.pk}/like/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_like_post_success(self):
        self.client.force_authenticate(user=self.liker)
        response = self.client.post(f"/api/posts/{self.post.pk}/like/")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Like.objects.filter(post=self.post, user=self.liker).exists())
        self.assertIn("post_id", response.data)

    def test_like_post_duplicate_returns_400(self):
        self.client.force_authenticate(user=self.liker)
        self.client.post(f"/api/posts/{self.post.pk}/like/")
        response = self.client.post(f"/api/posts/{self.post.pk}/like/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already liked", response.data["detail"].lower())

    def test_unlike_post_success(self):
        Like.objects.create(post=self.post, user=self.liker)
        self.client.force_authenticate(user=self.liker)
        response = self.client.post(f"/api/posts/{self.post.pk}/unlike/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Like.objects.filter(post=self.post, user=self.liker).exists())

    def test_unlike_when_not_liked_returns_400(self):
        self.client.force_authenticate(user=self.liker)
        response = self.client.post(f"/api/posts/{self.post.pk}/unlike/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_like_creates_notification_for_author(self):
        from notifications.models import Notification

        self.client.force_authenticate(user=self.liker)
        self.client.post(f"/api/posts/{self.post.pk}/like/")
        notif = Notification.objects.filter(
            recipient=self.author, verb="liked your post", actor=self.liker
        ).first()
        self.assertIsNotNone(notif)
        self.assertFalse(notif.is_read)

    def test_like_own_post_does_not_create_notification(self):
        from notifications.models import Notification

        initial_count = Notification.objects.filter(verb="liked your post").count()
        self.client.force_authenticate(user=self.author)
        self.client.post(f"/api/posts/{self.post.pk}/like/")
        self.assertEqual(
            Notification.objects.filter(verb="liked your post").count(),
            initial_count,
        )
