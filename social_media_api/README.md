# Social Media API

A REST API for a social media platform, built with Django and Django REST Framework. It provides user registration, token-based authentication, and profile management.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install django djangorestframework Pillow
```

### 2. Apply migrations

From the project root (`social_media_api/`):

```bash
python manage.py migrate
```

This creates the custom User table and the auth token tables.

### 3. (Optional) Create a superuser

```bash
python manage.py createsuperuser
```

### 4. Run the development server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`. Account endpoints are under `http://127.0.0.1:8000/api/accounts/`.

---

## User model overview

The API uses a **custom user model** (`accounts.User`) that extends Django’s `AbstractUser` with:

| Field             | Type        | Description                                      |
|-------------------|------------|--------------------------------------------------|
| `username`        | str        | Required, unique (from AbstractUser)             |
| `email`           | str        | Optional (from AbstractUser)                      |
| `password`        | str        | Hashed (from AbstractUser)                       |
| `first_name`      | str        | Optional (from AbstractUser)                     |
| `last_name`       | str        | Optional (from AbstractUser)                     |
| `bio`             | text       | Optional biography / about section               |
| `profile_picture` | image      | Optional; uploaded to `profile_pictures/`       |
| `followers`       | M2M (self) | Users who follow this user (`symmetrical=False`) |

Related name `following` is used for the reverse relation (users this user follows). Helper methods on the model include `follower_count()`, `following_count()`, `is_following(user)`, `follow(user)`, and `unfollow(user)`.

---

## Register and authenticate

Authentication is **token-based**. Register or log in to receive a token; send it in the `Authorization` header for protected endpoints.

### Base URL for account endpoints

- Base: `http://127.0.0.1:8000/api/accounts/`

### 1. Register

**Endpoint:** `POST /api/accounts/register/`

**Body (JSON):**

- `username` (required)
- `email` (optional)
- `password` (required, min 8 characters)
- `first_name`, `last_name`, `bio`, `profile_picture` (optional)

**Example:**

```bash
curl -X POST http://127.0.0.1:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"jane","email":"jane@example.com","password":"securepass123"}'
```

**Success response (201):**

```json
{
  "token": "9944b09199c62b9418...",
  "user": {
    "id": 1,
    "username": "jane",
    "email": "jane@example.com",
    "first_name": "",
    "last_name": "",
    "bio": null,
    "profile_picture": null,
    "follower_count": 0,
    "following_count": 0
  }
}
```

Save the `token` value for later requests.

### 2. Login

**Endpoint:** `POST /api/accounts/login/`

**Body (JSON):**

- `username`
- `password`

**Example:**

```bash
curl -X POST http://127.0.0.1:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"jane","password":"securepass123"}'
```

**Success response (200):**

```json
{
  "token": "9944b09199c62b9418...",
  "user": { ... }
}
```

### 3. Use the token (profile)

**Endpoint:** `GET` or `PUT`/`PATCH` `/api/accounts/profile/`

**Headers:**

- `Authorization: Token <your-token-key>`

**Example (get profile):**

```bash
curl -X GET http://127.0.0.1:8000/api/accounts/profile/ \
  -H "Authorization: Token 9944b09199c62b9418..."
```

**Example (update profile):**

```bash
curl -X PATCH http://127.0.0.1:8000/api/accounts/profile/ \
  -H "Authorization: Token 9944b09199c62b9418..." \
  -H "Content-Type: application/json" \
  -d '{"bio":"Hello, I am Jane."}'
```

---

## Testing with Postman

1. **Register:** Create a request to `POST {{base}}/api/accounts/register/` with a JSON body (`username`, `password`, optional `email`). Check that the response contains `token` and `user`.
2. **Login:** `POST {{base}}/api/accounts/login/` with `username` and `password`. Confirm you receive the same `token` and `user` format.
3. **Profile:** For `GET` and `PATCH` to `/api/accounts/profile/`, add header `Authorization` with value `Token <paste-token-here>`. Verify you can read and update the authenticated user’s profile.

---

## Posts and Comments API

Base URL for posts and comments: `http://127.0.0.1:8000/api/`

### Authentication

- **List** (GET) posts and comments: no authentication required.
- **Create** (POST): requires `Authorization: Token <token>`.
- **Update/Delete** (PUT, PATCH, DELETE): requires authentication and **only the author** of the post or comment can modify or delete it.

### Pagination

List endpoints return paginated results (10 items per page by default). Use query parameters:

- `?page=2` – next page
- `?page_size=10` – (if supported) page size

Response format:

```json
{
  "count": 50,
  "next": "http://127.0.0.1:8000/api/posts/?page=2",
  "previous": null,
  "results": [ ... ]
}
```

### Posts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/posts/` | List all posts (paginated). **Search:** `?search=<query>` matches title and content. |
| POST | `/api/posts/` | Create a post (auth required). Author is set to the current user. |
| GET | `/api/posts/<id>/` | Retrieve a single post (includes nested comments). |
| PUT/PATCH | `/api/posts/<id>/` | Update a post (author only). |
| DELETE | `/api/posts/<id>/` | Delete a post (author only). |

**Create post – request body (JSON):**

```json
{
  "title": "My first post",
  "content": "Hello, world!"
}
```

**Create post – example:**

```bash
curl -X POST http://127.0.0.1:8000/api/posts/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My first post","content":"Hello, world!"}'
```

**Search posts – example:**

```bash
curl "http://127.0.0.1:8000/api/posts/?search=hello"
```

**Retrieve post – response (200):**

```json
{
  "id": 1,
  "author": "jane",
  "title": "My first post",
  "content": "Hello, world!",
  "created_at": "2026-02-21T12:00:00Z",
  "updated_at": "2026-02-21T12:00:00Z",
  "comments": [
    {
      "id": 1,
      "post": 1,
      "author": "john",
      "content": "Nice post!",
      "created_at": "2026-02-21T12:05:00Z",
      "updated_at": "2026-02-21T12:05:00Z"
    }
  ]
}
```

### Comments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/comments/` | List all comments (paginated). **Filter:** `?post=<post_id>` to list comments for a post. |
| POST | `/api/comments/` | Create a comment (auth required). Author is set to the current user. |
| GET | `/api/comments/<id>/` | Retrieve a single comment. |
| PUT/PATCH | `/api/comments/<id>/` | Update a comment (author only). |
| DELETE | `/api/comments/<id>/` | Delete a comment (author only). |

**Create comment – request body (JSON):**

```json
{
  "post": 1,
  "content": "Great post!"
}
```

**Create comment – example:**

```bash
curl -X POST http://127.0.0.1:8000/api/comments/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"post":1,"content":"Great post!"}'
```

**List comments for a post – example:**

```bash
curl "http://127.0.0.1:8000/api/comments/?post=1"
```

**Retrieve comment – response (200):**

```json
{
  "id": 1,
  "post": 1,
  "author": "john",
  "content": "Great post!",
  "created_at": "2026-02-21T12:05:00Z",
  "updated_at": "2026-02-21T12:05:00Z"
}
```

### Testing posts and comments (Postman)

1. **List posts:** GET `/api/posts/` – no auth. Check pagination and try `?search=keyword`.
2. **Create post:** POST `/api/posts/` with header `Authorization: Token <token>` and body `{"title":"Test","content":"Body"}`. Expect 201 and post in response.
3. **Update/delete post:** As the post author, PATCH/DELETE `/api/posts/<id>/`. As another user, expect 403.
4. **List comments:** GET `/api/comments/` and GET `/api/comments/?post=1`. Check pagination.
5. **Create comment:** POST `/api/comments/` with `{"post": 1, "content": "Comment text"}` and auth header. Expect 201.
6. **Update/delete comment:** As the comment author, PATCH/DELETE `/api/comments/<id>/`. As another user, expect 403.

---

## Project structure

- `social_media_api/` – Django project (settings, root URLs).
- `accounts/` – App for user model, registration, login, and profile (serializers, views, URLs).
- `posts/` – App for Post and Comment models, ViewSets, serializers, permissions, and router URLs.
- Account API: `/api/accounts/` (register, login, profile).
- Posts and comments API: `/api/posts/`, `/api/comments/` (with pagination and search/filter).
