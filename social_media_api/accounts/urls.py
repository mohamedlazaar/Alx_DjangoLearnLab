from django.urls import path
from .views import RegisterView, CustomObtainAuthToken, ProfileView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
	path('register/', RegisterView.as_view(), name='register'),
	path('login/', CustomObtainAuthToken.as_view(), name='login'),
	path('profile/', ProfileView.as_view(), name='profile'),
]

