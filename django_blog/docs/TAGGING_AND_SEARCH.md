# Tagging and Search – Documentation

This document describes how to use tags on posts and how to search the blog by title, content, or tags.

## Tagging

### Model

- **Tag:** `name` (unique), `slug` (unique, auto-generated from name for URLs).
- **Post:** Many-to-many with `Tag` via the `tags` field (a post can have many tags; a tag can be on many posts).

### Adding and editing tags on a post

1. When **creating** or **editing** a post, use the **Tags** field.
2. Enter tags as a **comma-separated** list (e.g. `python, django, tutorial`).
3. If a tag name does not exist, it is **created** automatically. Existing tags are reused.
4. Leave the field empty to have no tags. When editing, clear the field and save to remove all tags from the post.

Only authenticated post authors can create/edit posts and thus manage tags.

### Where tags appear

- **Post list** (`/posts/`): Under each post title, tags are shown as links.
- **Post detail** (`/posts/<id>/`): Under the post meta, tags are shown as links.
- **Home** (`/`): Same as list, tags under each snippet.

### Viewing posts by tag

- Click any tag link (e.g. on a post). You are taken to **`/tags/<slug>/`**, which lists all posts that have that tag.
- Example: tag "django" with slug `django` → `/tags/django/`.

---

## Search

### How to search

1. Use the **search bar** in the site header (on every page).
2. Type a **keyword** or phrase and submit (e.g. "django", "tutorial").
3. You are taken to **`/search/?q=<query>`**, which shows the **search results** page.

### What is searched

The search uses Django **Q objects** to match the query against:

- **Post title** (case-insensitive)
- **Post content** (case-insensitive)
- **Tag names** (case-insensitive)

Matches are combined with OR: a post appears if the query appears in **any** of these.

### Search results page

- **URL:** `/search/` (GET parameter `q` for the query).
- Shows all matching posts (title, author, date, tags, snippet).
- If `q` is empty, the page asks you to enter a search term.
- If there are no matches, a short “no results” message is shown.

---

## URL reference

| Path | Description |
|------|-------------|
| `/search/` | Search form and results (GET `q` = search query). |
| `/tags/<tag_slug>/` | List of posts that have the tag with that slug. |

---

## Implementation notes

- **PostForm** includes a `tags_input` CharField (comma-separated). On save, the string is parsed, each name is normalized (strip), and tags are **get_or_create**d by name; the post’s `tags` M2M is then set. New tags get a slug from their name (e.g. via `slugify`).
- **Search view** uses `Q(title__icontains=q) | Q(content__icontains=q) | Q(tags__name__icontains=q)` and `.distinct()` so each post appears once.
- **Tag view** filters posts by `tags=tag` (tag looked up by `slug`).

---

## Testing checklist

- Create a post with tags `python, django`; confirm tags appear on list and detail and that new tags were created.
- Edit the post: add a tag, remove a tag, clear all tags; confirm persistence.
- Click a tag link; confirm the tag page lists only posts with that tag.
- Search for a word in a title; for a word in content; for a tag name; confirm correct posts and no duplicates.
- Empty search and invalid/missing query: confirm the search page still loads and shows the expected message.
