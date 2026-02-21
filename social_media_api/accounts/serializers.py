from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField()
    # extra_kwargs apply write_only and min_length to password
    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "first_name", "last_name", "bio", "profile_picture")
        extra_kwargs = {"password": {"write_only": True, "min_length": 8}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = get_user_model().objects.create_user(password=password, **validated_data)
        Token.objects.create(user=user)
        return user


class UserSerializer(serializers.ModelSerializer):
    follower_count = serializers.SerializerMethodField(read_only=True)
    following_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "bio", "profile_picture", "follower_count", "following_count")
        read_only_fields = ("id", "follower_count", "following_count")

    def get_follower_count(self, obj):
        return obj.follower_count()

    def get_following_count(self, obj):
        return obj.following_count()
