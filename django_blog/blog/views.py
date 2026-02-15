"""
Blog and authentication views.

CRUD for posts: ListView, DetailView (public); CreateView (authenticated);
UpdateView, DeleteView (author only via UserPassesTestMixin).
"""
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import CommentForm, CustomUserCreationForm, PostForm, UserProfileForm
from .models import Comment, Post, UserProfile


def home(request):
    """Home page: list of posts (or placeholder)."""
    posts = Post.objects.all().select_related("author").order_by("-published_date")[:10]
    return render(request, "blog/home.html", {"posts": posts})


# --- Post CRUD (class-based views) ---


class PostListView(ListView):
    """Display all blog posts. Accessible to everyone."""
    model = Post
    context_object_name = "posts"
    template_name = "blog/post_list.html"
    ordering = ["-published_date"]
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().select_related("author")


class PostDetailView(DetailView):
    """Display a single blog post and its comments. Accessible to everyone."""
    model = Post
    context_object_name = "post"
    template_name = "blog/post_detail.html"

    def get_queryset(self):
        return super().get_queryset().select_related("author")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = self.object.comments.select_related("author").all()
        context["comment_form"] = CommentForm()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Create a new post. Only authenticated users."""
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    success_url = reverse_lazy("blog:post_list")
    login_url = "blog:login"

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Post created successfully.")
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Edit an existing post. Only the author can edit."""
    model = Post
    form_class = PostForm
    context_object_name = "post"
    template_name = "blog/post_form.html"
    success_url = reverse_lazy("blog:post_list")
    login_url = "blog:login"

    def test_func(self):
        return self.get_object().author == self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Post updated successfully.")
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a post. Only the author can delete."""
    model = Post
    context_object_name = "post"
    template_name = "blog/post_confirm_delete.html"
    success_url = reverse_lazy("blog:post_list")
    login_url = "blog:login"

    def test_func(self):
        return self.get_object().author == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Post deleted successfully.")
        return super().delete(request, *args, **kwargs)


# --- Comment views ---


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Create a comment on a post. Authenticated only; redirects back to post detail."""
    model = Comment
    form_class = CommentForm
    login_url = "blog:login"

    def dispatch(self, request, *args, **kwargs):
        post_id = kwargs.get("post_id") or kwargs.get("pk")
        self.post_obj = get_object_or_404(Post, pk=post_id)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return redirect("blog:post_detail", pk=self.post_obj.pk)

    def form_valid(self, form):
        form.instance.post = self.post_obj
        form.instance.author = self.request.user
        messages.success(self.request, "Comment added.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.post_obj.pk})


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Edit a comment. Only the comment author can edit."""
    model = Comment
    form_class = CommentForm
    context_object_name = "comment"
    template_name = "blog/comment_form.html"
    login_url = "blog:login"
    pk_url_kwarg = "comment_pk"

    def get_object(self, queryset=None):
        pk = self.kwargs.get("comment_pk") or self.kwargs.get("pk")
        return get_object_or_404(Comment, pk=pk)

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.get_object().post_id})

    def form_valid(self, form):
        messages.success(self.request, "Comment updated.")
        return super().form_valid(form)


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a comment. Only the comment author can delete."""
    model = Comment
    context_object_name = "comment"
    template_name = "blog/comment_confirm_delete.html"
    login_url = "blog:login"
    pk_url_kwarg = "comment_pk"

    def get_object(self, queryset=None):
        pk = self.kwargs.get("comment_pk") or self.kwargs.get("pk")
        return get_object_or_404(Comment, pk=pk)

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.get_object().post_id})

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Comment deleted.")
        return super().delete(request, *args, **kwargs)


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
