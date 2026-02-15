"""
Blog and authentication views.
"""
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import CustomUserCreationForm, UserProfileForm
from .models import Post, UserProfile


def home(request):
    """Home page: list of posts (or placeholder)."""
    posts = Post.objects.all().select_related("author").order_by("-published_date")[:10]
    return render(request, "blog/home.html", {"posts": posts})


class BlogLoginView(LoginView):
    """Django built-in login view with custom template."""
    template_name = "blog/login.html"
    redirect_authenticated_user = True


class BlogLogoutView(LogoutView):
    """Django built-in logout view; redirect to logged-out confirmation page."""
    next_page = reverse_lazy("blog:logged_out")


def logged_out(request):
    """Confirmation page after logout (linked from LogoutView redirect)."""
    return render(request, "blog/logged_out.html")


def register(request):
    """User registration using CustomUserCreationForm (includes email)."""
    if request.user.is_authenticated:
        return redirect("blog:home")
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully. You are now logged in.")
            return redirect("blog:home")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, "blog/register.html", {"form": form})


@login_required
def profile_view(request):
    """View and edit profile. Handles GET (display) and POST (update)."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = UserProfileForm(
            request.POST, request.FILES, instance=profile
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("blog:profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserProfileForm(instance=profile)
    return render(request, "blog/profile.html", {"form": form, "profile": profile})
