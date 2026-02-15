"""
Blog app URL configuration.

Authentication:
- /           - home
- /login/     - login
- /logout/    - logout
- /register/  - registration
- /profile/   - profile view/edit (authenticated)

Post CRUD:
- /posts/               - list all posts
- /posts/new/           - create post (authenticated)
- /posts/<pk>/          - post detail
- /posts/<pk>/edit/     - edit post (author only)
- /posts/<pk>/delete/   - delete post (author only)
"""
from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.BlogLoginView.as_view(), name="login"),
    path("logout/", views.BlogLogoutView.as_view(), name="logout"),
    path("logged-out/", views.logged_out, name="logged_out"),
    path("register/", views.register, name="register"),
    path("profile/", views.profile_view, name="profile"),
    # Post CRUD
    path("posts/", views.PostListView.as_view(), name="post_list"),
    path("posts/new/", views.PostCreateView.as_view(), name="post_create"),
    path("posts/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("posts/<int:pk>/edit/", views.PostUpdateView.as_view(), name="post_update"),
    path("posts/<int:pk>/delete/", views.PostDeleteView.as_view(), name="post_delete"),
]
