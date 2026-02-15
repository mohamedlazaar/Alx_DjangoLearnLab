# Blog Post CRUD – Documentation

This document describes the blog post management features: create, read, update, and delete (CRUD) for the `Post` model.

## Overview

- **List:** All users can view the list of posts at `/posts/`.
- **Detail:** All users can view a single post at `/posts/<id>/`.
- **Create:** Only authenticated users can create posts at `/posts/new/`. The author is set to the logged-in user.
- **Update:** Only the **author** of a post can edit it at `/posts/<id>/edit/`.
- **Delete:** Only the **author** of a post can delete it at `/posts/<id>/delete/` (after confirming).

Permissions are enforced with Django’s `LoginRequiredMixin` (create, update, delete) and `UserPassesTestMixin` (update, delete: `request.user == post.author`). List and detail views are public.

## URL Routes

| Path | Name | Description | Access |
|------|------|-------------|--------|
| `/posts/` | `blog:post_list` | List all posts (paginated) | Everyone |
| `/posts/new/` | `blog:post_create` | Create a new post | Authenticated |
| `/posts/<pk>/` | `blog:post_detail` | View one post | Everyone |
| `/posts/<pk>/edit/` | `blog:post_update` | Edit post | Author only |
| `/posts/<pk>/delete/` | `blog:post_delete` | Delete post (with confirmation) | Author only |

## Implementation Details

### Views (`blog/views.py`)

- **PostListView:** `ListView`; queryset ordered by `-published_date`, `select_related("author")`, pagination (10 per page).
- **PostDetailView:** `DetailView`; single post with author.
- **PostCreateView:** `LoginRequiredMixin`, `CreateView`; uses `PostForm`; in `form_valid()`, sets `form.instance.author = request.user` and shows a success message.
- **PostUpdateView:** `LoginRequiredMixin`, `UserPassesTestMixin`, `UpdateView`; `test_func()` returns `self.get_object().author == self.request.user`; success message on save.
- **PostDeleteView:** `LoginRequiredMixin`, `UserPassesTestMixin`, `DeleteView`; same `test_func`; confirmation template; success message on delete.

Unauthorized users (e.g. non-author opening edit/delete) receive a 403 Forbidden via `UserPassesTestMixin`.

### Form (`blog/forms.py`)

- **PostForm:** `ModelForm` for `Post` with fields `title` and `content` only. Author is not in the form; it is set in `PostCreateView.form_valid()`. Used for both create and update.

### Templates

- **post_list.html:** List of posts with title (linked to detail), author, date, and content snippet. “New Post” button for authenticated users. Pagination controls when needed.
- **post_detail.html:** Full post (title, author, date, content). For the author only: “Edit” and “Delete” links.
- **post_form.html:** Single form template for both create and edit; title and content fields; submit and cancel.
- **post_confirm_delete.html:** Confirmation message and a POST form to confirm deletion; cancel link back to post detail.

All forms include `{% csrf_token %}` for CSRF protection.

### Data and Validation

- **Title:** Required, max 200 characters (model).
- **Content:** Required (model).
- **Author:** Set automatically on create; cannot be changed via the form. Only the author can edit/delete (enforced in the view).
- **published_date:** Set automatically on creation (`auto_now_add=True` on the model).

## How to Use

1. **View posts:** Open “Posts” in the nav or go to `/posts/`. Click a post title to open its detail page.
2. **Create a post:** Log in, then click “New Post” or go to `/posts/new/`. Fill title and content, submit. You are redirected to the post list with a success message.
3. **Edit a post:** Open the post detail page; if you are the author, click “Edit”. Change title/content and submit, or cancel to go back to the list.
4. **Delete a post:** On the post detail page, click “Delete”. On the confirmation page, submit to delete or cancel to return to the post. Deletion is permanent.

## Testing Checklist

- **List:** Open `/posts/` as anonymous and as logged-in user; posts and “New Post” (when logged in) appear.
- **Detail:** Open `/posts/<id>/`; full post and, for author, Edit/Delete links.
- **Create:** As guest, `/posts/new/` should redirect to login. After login, create a post; author is set and post appears in list/detail.
- **Update:** As author, edit post and save; changes appear. As another user, opening `/posts/<id>/edit/` for someone else’s post should return 403.
- **Delete:** As author, delete from detail → confirm; post is removed. As another user, `/posts/<id>/delete/` for someone else’s post should return 403.
- **Navigation:** Home, Posts, New Post, and post links in list/detail all work and match the URL table above.

## File Reference

- **Views:** `blog/views.py` (PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView)
- **Form:** `blog/forms.py` (PostForm)
- **URLs:** `blog/urls.py` (post_list, post_create, post_detail, post_update, post_delete)
- **Templates:** `blog/templates/blog/post_list.html`, `post_detail.html`, `post_form.html`, `post_confirm_delete.html`
