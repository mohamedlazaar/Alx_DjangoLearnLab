from rest_framework import serializers

from .models import Comment, Like, Post


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
    like_count = serializers.SerializerMethodField()
    liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id", "author", "title", "content",
            "created_at", "updated_at", "comments", "like_count", "liked_by_user",
        ]
        read_only_fields = ["id", "author", "created_at", "updated_at"]

    def get_like_count(self, obj):
        return getattr(obj, "_like_count", obj.likes.count())

    def get_liked_by_user(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return getattr(obj, "_liked_by_user", obj.likes.filter(user=request.user).exists())


class PostListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view (no nested comments)."""

    author = serializers.StringRelatedField(read_only=True)
    like_count = serializers.SerializerMethodField()
    liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id", "author", "title", "content",
            "created_at", "updated_at", "like_count", "liked_by_user",
        ]

    def get_like_count(self, obj):
        return getattr(obj, "_like_count", obj.likes.count())

    def get_liked_by_user(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return getattr(obj, "_liked_by_user", obj.likes.filter(user=request.user).exists())