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

## Project structure

- `social_media_api/` – Django project (settings, root URLs).
- `accounts/` – App for user model, registration, login, and profile (serializers, views, URLs).
- Account API routes are mounted at `/api/accounts/` (register, login, profile).
