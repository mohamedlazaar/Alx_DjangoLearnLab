from rest_framework import serializers

from .models import Comment, Post


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment. User (author) is set in the view."""

    author = serializers.StringRelatedField(source="user", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "post", "author", "content", "created_at", "updated_at"]
        read_only_fields = ["id", "author", "created_at", "updated_at"]


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post. Author is set in the view on create."""

    author = serializers.StringRelatedField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ["id", "author", "title", "content", "created_at", "updated_at", "comments"]
        read_only_fields = ["id", "author", "created_at", "updated_at"]


class PostListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view (no nested comments)."""

    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = ["id", "author", "title", "content", "created_at", "updated_at"]