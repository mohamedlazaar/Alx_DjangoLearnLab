"""
Authentication, profile, and blog post forms.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Comment, Post, UserProfile


class CommentForm(forms.ModelForm):
    """ModelForm for creating and updating comments. Author is set in the view."""

    class Meta:
        model = Comment
        fields = ("content",)
        widgets = {
            "content": forms.Textarea(attrs={"rows": 3, "placeholder": "Write a comment..."}),
        }
        labels = {"content": ""}


class PostForm(forms.ModelForm):
    """
    ModelForm for creating and updating blog posts.
    Fields: title, content. Author is set in the view from request.user.
    """

    class Meta:
        model = Post
        fields = ("title", "content")
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Post title"}),
            "content": forms.Textarea(attrs={"rows": 12, "placeholder": "Write your post content here..."}),
        }


class CustomUserCreationForm(UserCreationForm):
    """Registration form extending UserCreationForm to include email."""
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            UserProfile.objects.get_or_create(user=user)
        return user


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile and optional User fields."""
    email = forms.EmailField(required=True)

    class Meta:
        model = UserProfile
        fields = ("bio", "avatar")
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields["email"].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.user.email = self.cleaned_data["email"]
        if commit:
            profile.user.save()
            profile.save()
        return profile
