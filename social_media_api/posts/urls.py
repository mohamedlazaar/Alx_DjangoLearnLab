"""
URL routing for posts and comments using DRF routers.
- /posts/          list, create
- /posts/<id>/     retrieve, update, destroy
- /comments/       list (optional ?post=<id>), create
- /comments/<id>/  retrieve, update, destroy
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, PostViewSet

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")
router.register(r"comments", CommentViewSet, basename="comment")

urlpatterns = [
    path("", include(router.urls)),
]
