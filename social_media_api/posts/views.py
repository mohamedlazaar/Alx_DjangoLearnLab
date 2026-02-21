"""
ViewSets for Post and Comment with CRUD, pagination, and search.
Only the author can edit or delete their own posts and comments.
"""
from rest_framework import permissions
from rest_framework.filters import SearchFilter
from rest_framework import viewsets

from .models import Comment, Post
from .permissions import IsOwnerOrReadOnly
from .serializers import CommentSerializer, PostListSerializer, PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Post: list, create, retrieve, update, destroy.
    List is searchable by title and content. Only the author can update/delete.
    """

    queryset = Post.objects.all().select_related("author").order_by("-created_at")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ["title", "content"]

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
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
        serializer.save(user=self.request.user)
