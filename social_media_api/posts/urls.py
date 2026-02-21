"""
URL routing for posts, comments, and feed.
Feed endpoint: /feed/
- /feed/           list posts from followed users (auth required)
- /posts/          list, create
- /posts/<id>/     retrieve, update, destroy
- /comments/       list (optional ?post=<id>), create
- /comments/<id>/  retrieve, update, destroy
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CommentViewSet,
    FeedView,
    PostLikeView,
    PostUnlikeView,
    PostViewSet,
)

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")
router.register(r"comments", CommentViewSet, basename="comment")

urlpatterns = [
    path("feed/", FeedView.as_view(), name="feed"),
    path("posts/<int:pk>/like/", PostLikeView.as_view(), name="post-like"),
    path("posts/<int:pk>/unlike/", PostUnlikeView.as_view(), name="post-unlike"),
    path("", include(router.urls)),
]
