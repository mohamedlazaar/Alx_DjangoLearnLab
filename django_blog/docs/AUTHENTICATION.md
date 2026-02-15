# Django Blog – Authentication System

This document describes the user authentication system: registration, login, logout, and profile management.

## Overview

- **Login / Logout:** Django’s built-in `LoginView` and `LogoutView` with custom templates.
- **Registration:** Custom view and form extending `UserCreationForm` to include email.
- **Profile:** Custom view and form to view and edit profile (email, bio, optional avatar). All forms use CSRF protection and Django’s default password hashing.

## Setup

1. **Migrations (required after adding `UserProfile`):**
   ```bash
   python manage.py makemigrations blog
   python manage.py migrate
   ```

2. **Media files (profile pictures):**  
   In development, media are served when `DEBUG=True` (see `django_blog/urls.py`).  
   For production, serve `MEDIA_ROOT` with your web server.  
   **Profile picture (avatar):** Install Pillow so `ImageField` works:  
   `pip install Pillow`

3. **Settings:**  
   - `LOGIN_URL = "blog:login"`  
   - `LOGIN_REDIRECT_URL = "blog:home"`  
   - `LOGOUT_REDIRECT_URL = "blog:logged_out"`  
   - `MEDIA_URL` / `MEDIA_ROOT` for user uploads.

## URL Routes

| Path         | Name          | Description                    | Auth required |
|-------------|----------------|--------------------------------|---------------|
| `/`         | `blog:home`    | Home (post list)               | No            |
| `/login/`   | `blog:login`   | Log in                         | No            |
| `/logout/`  | `blog:logout`  | Log out                        | Yes           |
| `/logged-out/` | `blog:logged_out` | “You have been logged out” page | No         |
| `/register/`| `blog:register`| Create account                 | No            |
| `/profile/` | `blog:profile` | View/edit profile              | Yes           |

## How It Works

### Registration

1. User opens `/register/`.
2. Submits the form (username, email, password1, password2).
3. `CustomUserCreationForm` validates and creates a `User`; a `UserProfile` is created via `get_or_create`.
4. User is logged in and redirected to home; a success message is shown.

### Login

1. User opens `/login/`.
2. Submits username and password.
3. `BlogLoginView` (Django’s `LoginView`) authenticates; on success, redirects to `blog:home`.
4. Invalid credentials: form is re-displayed with errors.

### Logout

1. User clicks “Logout” (or visits `/logout/`).
2. `BlogLogoutView` (Django’s `LogoutView`) logs the user out and redirects to `blog:logged_out`.
3. “You have been logged out” page is shown with links to log in again or home.

### Profile

1. Authenticated user opens `/profile/`.
2. **GET:** Current profile (email, bio, avatar) is shown in a form.
3. **POST:** Form is validated; user’s email and profile (bio, avatar) are updated; success message and redirect to `/profile/`.

### Security

- All forms use `{% csrf_token %}` (CSRF protection).
- Passwords are hashed with Django’s default (PBKDF2); never stored in plain text.
- Profile and logout are behind authentication; `@login_required` is used for the profile view.
- File uploads (avatar) use `ImageField` and optional validation (e.g. Pillow); restrict file types/size in production if needed.

## Testing Each Feature

Run the dev server:

```bash
python manage.py runserver
```

1. **Registration**
   - Go to `/register/`.
   - Fill username, email, password (twice). Submit.
   - Expect redirect to home and “Account created successfully.”
   - Try duplicate username or invalid email to see validation errors.

2. **Login**
   - Log out (or use an incognito window). Go to `/login/`.
   - Enter valid credentials; expect redirect to home.
   - Enter wrong password; expect error and form re-display.

3. **Logout**
   - While logged in, click “Logout” or open `/logout/`.
   - Expect redirect to “You have been logged out” and no longer logged in.

4. **Profile**
   - Log in, go to `/profile/`.
   - Change email and/or bio (and optionally upload an avatar). Submit.
   - Expect “Profile updated successfully” and updated data on next load.
   - Without logging in, open `/profile/`; expect redirect to login.

## Code Layout

- **Models:** `blog/models.py` – `UserProfile` (OneToOne to User, bio, avatar).
- **Forms:** `blog/forms.py` – `CustomUserCreationForm`, `UserProfileForm`.
- **Views:** `blog/views.py` – `home`, `BlogLoginView`, `BlogLogoutView`, `register`, `profile_view`, `logged_out`.
- **URLs:** `blog/urls.py` – all auth and home routes; included in `django_blog/urls.py` at `""`.
- **Templates:** `blog/templates/blog/` – `base.html`, `home.html`, `login.html`, `register.html`, `profile.html`, `logged_out.html`.
- **Static:** `blog/static/blog/css/styles.css` – styles for forms and messages.

## Optional: Extending the Profile

To add more profile fields (e.g. “website”, “location”):

1. Add fields to `UserProfile` in `blog/models.py`.
2. Run `makemigrations` and `migrate`.
3. Add the fields to `UserProfileForm.Meta.fields` in `blog/forms.py`.
4. Optionally add them to `UserProfileAdmin` in `blog/admin.py`.
