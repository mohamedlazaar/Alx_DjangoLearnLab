"""
Basic API tests for posts and comments.
Run: python manage.py test posts
"""
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Comment, Post

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
