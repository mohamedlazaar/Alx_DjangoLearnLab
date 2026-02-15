"""
Blog app URL configuration.

Authentication and main routes:
- /           - home (post list)
- /login/     - login
- /logout/    - logout
- /register/  - registration
- /profile/   - profile view/edit (authenticated)
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
]
