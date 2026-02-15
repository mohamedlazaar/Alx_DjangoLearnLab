# Comment System – Documentation

This document describes the blog comment feature: how comments are stored, how to add/edit/delete them, and how permissions work.

## Overview

- **Read:** All users can see comments on a post (on the post detail page).
- **Add:** Only **authenticated** users can post a comment (form on the post detail page).
- **Edit:** Only the **comment author** can edit their comment.
- **Delete:** Only the **comment author** can delete their comment.

Permissions are enforced with `LoginRequiredMixin` (create) and `UserPassesTestMixin` (edit/delete: `request.user == comment.author`).

## Model: Comment

- **post** – `ForeignKey` to `Post` (many-to-one).
- **author** – `ForeignKey` to Django’s `User`.
- **content** – `TextField` (comment text).
- **created_at** – `DateTimeField(auto_now_add=True)`.
- **updated_at** – `DateTimeField(auto_now=True)`.

Comments are ordered by `created_at` (oldest first).

## URL Routes

| Path | Name | Description | Access |
|------|------|-------------|--------|
| (comments shown on post detail) | – | List of comments for a post | Everyone |
| `/posts/<post_id>/comments/new/` | `blog:comment_create` | Create a comment | Authenticated |
| `/posts/<post_id>/comments/<comment_pk>/edit/` | `blog:comment_update` | Edit a comment | Author only |
| `/posts/<post_id>/comments/<comment_pk>/delete/` | `blog:comment_delete` | Delete a comment | Author only |

## How to Use

### Viewing comments

- Open a post (e.g. `/posts/1/`). The “Comments” section lists all comments for that post (author, date, content). Edited comments show “(edited)” next to the date.

### Adding a comment

1. Log in.
2. Open the post.
3. Scroll to “Add a comment”.
4. Enter text and click “Post comment”.
5. You are redirected back to the same post; the new comment appears and a success message is shown.

If you are not logged in, you see “Log in to leave a comment” instead of the form.

### Editing a comment

1. Log in as the comment author.
2. On the post detail page, find your comment and click “Edit”.
3. On the edit page, change the text and click “Update comment”.
4. You are redirected back to the post; “(edited)” appears next to the comment date.

Only the author sees the “Edit” link. Other users get 403 if they open the edit URL.

### Deleting a comment

1. Log in as the comment author.
2. On the post detail page, click “Delete” on your comment (or go to the delete URL).
3. On the confirmation page, click “Yes, delete”.
4. You are redirected back to the post; the comment is removed.

Only the author can delete; others get 403.

## Visibility and Permissions

- **Visibility:** Comments are visible to everyone who can view the post (no separate “private” comments).
- **Create:** Requires authentication; author is set to the current user.
- **Edit/Delete:** Only the comment author; enforced in the view with `UserPassesTestMixin`. Unauthorized users get **403 Forbidden**.

## Implementation Summary

- **Form:** `CommentForm` (ModelForm, field: `content`). Author and post are set in the view.
- **Views:** `CommentCreateView` (LoginRequiredMixin), `CommentUpdateView`, `CommentDeleteView` (LoginRequiredMixin + UserPassesTestMixin). Create redirects GET to post detail; POST creates and redirects back to post.
- **Templates:** Comments and add form are in `post_detail.html`. Edit uses `comment_form.html`; delete uses `comment_confirm_delete.html`. All forms use `{% csrf_token %}`.

## Testing Checklist

- View a post: comments are listed; count is correct.
- Anonymous: no “Add a comment” form; “Log in to leave a comment” is shown.
- Logged in: add a comment; it appears and author/date are correct.
- As author: “Edit” and “Delete” visible; edit and delete work; redirect back to post.
- As another user: no Edit/Delete on others’ comments; direct URL to edit/delete returns 403.
- After edit: “(edited)” appears and `updated_at` is used where relevant.

## File Reference

- **Model:** `blog/models.py` – `Comment`
- **Form:** `blog/forms.py` – `CommentForm`
- **Views:** `blog/views.py` – `CommentCreateView`, `CommentUpdateView`, `CommentDeleteView`; `PostDetailView.get_context_data` adds `comments` and `comment_form`
- **URLs:** `blog/urls.py` – `comment_create`, `comment_update`, `comment_delete`
- **Templates:** `blog/templates/blog/post_detail.html` (comments + form), `comment_form.html`, `comment_confirm_delete.html`
