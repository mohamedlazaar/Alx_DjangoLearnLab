"""
ViewSets for Post and Comment with CRUD, pagination, and search.
Feed of posts from followed users. Like/unlike posts. Only the author can edit or delete.
"""
from django.db.models import Count, Exists, OuterRef
from rest_framework import permissions, status
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from notifications.utils import create_notification

from .models import Comment, Like, Post
from .permissions import IsOwnerOrReadOnly
from .serializers import CommentSerializer, PostListSerializer, PostSerializer


def _posts_queryset_with_likes(request):
    """Base post queryset with annotated like_count and liked_by_user."""
    qs = Post.objects.select_related("author").order_by("-created_at")
    if request and request.user.is_authenticated:
        qs = qs.annotate(
            _like_count=Count("likes"),
            _liked_by_user=Exists(Like.objects.filter(post=OuterRef("pk"), user=request.user)),
        )
    return qs


class FeedView(ListAPIView):
    """
    Feed of posts from users that the current user follows.
    Ordered by created_at descending (most recent first). Paginated. Requires authentication.
    """
    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        following_users = self.request.user.following.all()
        return _posts_queryset_with_likes(self.request).filter(
            author__in=following_users
        )


class PostViewSet(ModelViewSet):
    """
    ViewSet for Post: list, create, retrieve, update, destroy.
    List is searchable by title and content. Only the author can update/delete.
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ["title", "content"]

    def get_queryset(self):
        return _posts_queryset_with_likes(self.request)

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(ModelViewSet):
    """
    ViewSet for Comment: list, create, retrieve, update, destroy.
    Filter by post via query param ?post=<id>. Only the author can update/delete.
    """

    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = Comment.objects.all().select_related("user", "post").order_by("-created_at")
        post_id = self.request.query_params.get("post")
        if post_id:
            qs = qs.filter(post_id=post_id)
        return qs

    def perform_create(self, serializer):
        comment = serializer.save(user=self.request.user)
        # Notify post author (unless they commented on their own post)
        if comment.post.author_id != comment.user_id:
            create_notification(
                recipient=comment.post.author,
                verb="commented on your post",
                actor=self.request.user,
                target=comment.post,
            )


class PostLikeView(APIView):
    """Like a post. Requires authentication. Cannot like the same post twice."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if Like.objects.filter(post=post, user=request.user).exists():
            return Response(
                {"detail": "You have already liked this post."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Like.objects.create(post=post, user=request.user)
        # Notify post author (unless they liked their own post)
        if post.author_id != request.user.id:
            create_notification(
                recipient=post.author,
                verb="liked your post",
                actor=request.user,
                target=post,
            )
        return Response(
            {"detail": "Post liked.", "post_id": post.pk},
            status=status.HTTP_201_CREATED,
        )


class PostUnlikeView(APIView):
    """Remove your like from a post. Requires authentication."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        deleted, _ = Like.objects.filter(post=post, user=request.user).delete()
        if not deleted:
            return Response(
                {"detail": "You had not liked this post."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"detail": "Post unliked.", "post_id": post.pk})
