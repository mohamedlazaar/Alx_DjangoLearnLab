from django.urls import path

from .views import CustomObtainAuthToken, ProfileView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomObtainAuthToken.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
]

