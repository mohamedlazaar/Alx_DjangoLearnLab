from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()
CustomUser = get_user_model()


class RegisterView(generics.CreateAPIView):
	"""Register a new user and return token on success."""
	serializer_class = RegisterSerializer
	permission_classes = [permissions.AllowAny]

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.save()
		token, _ = Token.objects.get_or_create(user=user)
		data = UserSerializer(user, context={"request": request}).data
		return Response({"token": token.key, "user": data}, status=status.HTTP_201_CREATED)


class CustomObtainAuthToken(ObtainAuthToken):
	"""Login view that returns token and user data."""
	def post(self, request, *args, **kwargs):
		response = super().post(request, *args, **kwargs)
		token_key = response.data.get('token')
		try:
			token = Token.objects.get(key=token_key)
			user = token.user
			user_data = UserSerializer(user, context={"request": request}).data
			return Response({"token": token.key, "user": user_data})
		except Token.DoesNotExist:
			return Response({"detail": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the authenticated user's profile."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class FollowUserView(generics.GenericAPIView):
    """Follow another user. Authenticated user can only modify their own following list."""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CustomUser.objects.all()

    def post(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        target = get_object_or_404(CustomUser, pk=user_id)
        if target == request.user:
            return Response(
                {"detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.follow(target)
        return Response(
            {"detail": f"You are now following {target.username}."},
            status=status.HTTP_200_OK,
        )


class UnfollowUserView(generics.GenericAPIView):
    """Unfollow another user. Authenticated user can only modify their own following list."""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CustomUser.objects.all()

    def post(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        target = get_object_or_404(CustomUser, pk=user_id)
        request.user.unfollow(target)
        return Response(
            {"detail": f"You have unfollowed {target.username}."},
            status=status.HTTP_200_OK,
        )
