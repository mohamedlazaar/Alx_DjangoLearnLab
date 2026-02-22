# Social Media API – Deployment Guide

This document describes how to prepare and deploy the **social_media_api** Django REST API to a production environment.

---

## Table of Contents

1. [Project preparation](#1-project-preparation)
2. [Production settings overview](#2-production-settings-overview)
3. [Hosting options](#3-hosting-options)
4. [Web server and WSGI](#4-web-server-and-wsgi)
5. [Static and media files](#5-static-and-media-files)
6. [Database](#6-database)
7. [Environment variables](#7-environment-variables)
8. [Deploy steps (generic)](#8-deploy-steps-generic)
9. [Platform-specific notes](#9-platform-specific-notes)
10. [Monitoring and maintenance](#10-monitoring-and-maintenance)
11. [Final testing](#11-final-testing)

---

## 1. Project preparation

- **Repository:** Ensure the project is in a Git repository (e.g. GitHub/GitLab).
- **Dependencies:** `requirements.txt` includes Django, DRF, Pillow, Gunicorn, Whitenoise, and dj-database-url.
- **Secrets:** Never commit `.env` or real `SECRET_KEY`/`DATABASE_URL`; use `.env.example` as a template.

---

## 2. Production settings overview

The app uses a single `settings.py` that reads from the environment:

| Setting | Env variable | Production |
|--------|----------------|------------|
| `SECRET_KEY` | `DJANGO_SECRET_KEY` | Long random string (e.g. `secrets.token_urlsafe(50)`) |
| `DEBUG` | `DJANGO_DEBUG` | `False` |
| `ALLOWED_HOSTS` | `ALLOWED_HOSTS` | Comma-separated list of your domain(s) |
| Database | `DATABASE_URL` | PostgreSQL URL (or leave unset for SQLite only for small setups) |
| HTTPS redirect | `SECURE_SSL_REDIRECT` | `True` when the platform terminates SSL |
| CSRF trusted origins | `CSRF_TRUSTED_ORIGINS` | `https://yourdomain.com` (comma-separated) |

When `DEBUG=False`, the following are applied:

- `SECURE_BROWSER_XSS_FILTER = True`
- `SECURE_CONTENT_TYPE_NOSNIFF = True`
- `X_FRAME_OPTIONS = "DENY"`
- `SECURE_SSL_REDIRECT` (if enabled via env)
- `CSRF_COOKIE_SECURE` and `SESSION_COOKIE_SECURE = True`
- HSTS headers (subdomains and preload enabled)

Static files are served via **Whitenoise** (no separate static server required on PaaS). Optional file logging is documented in [Monitoring](#10-monitoring-and-maintenance).

---

## 3. Hosting options

Suitable options for this Django app:

| Service | Notes |
|--------|--------|
| **Heroku** | Use Procfile; add-ons for PostgreSQL. Set config vars in dashboard. |
| **Railway** | Connect repo; set env vars; add PostgreSQL from dashboard. |
| **Render** | Web Service + PostgreSQL; use Build Command and Start Command (see below). |
| **DigitalOcean App Platform** | Connect repo; add DB; set env. |
| **AWS Elastic Beanstalk** | Use a Procfile or `eb init`; RDS for DB. |
| **VPS (DigitalOcean Droplet, etc.)** | Install Python, Nginx, Gunicorn; use `nginx.conf.example` and a process manager (systemd). |

The project includes a **Procfile** for Heroku/Railway/Render-style platforms.

---

## 4. Web server and WSGI

- **WSGI server:** **Gunicorn** is in `requirements.txt`. The **Procfile** runs:
  ```bash
  web: gunicorn social_media_api.wsgi --bind 0.0.0.0:$PORT --workers 2 --threads 4 --log-level info
  ```
- **Reverse proxy (VPS):** Use **Nginx** in front of Gunicorn. Copy `nginx.conf.example` to your server and set:
  - `server_name`
  - `alias` paths for `/static/` and `/media/`
  - SSL certificate paths
  - `proxy_pass` to your Gunicorn bind (e.g. `127.0.0.1:8000`).

Local run (no Nginx):

```bash
gunicorn social_media_api.wsgi --bind 0.0.0.0:8000 --workers 2
```

---

## 5. Static and media files

- **Static:** Run `python manage.py collectstatic --noinput` before or during deployment. Whitenoise serves these in production; no separate static server is required on PaaS.
- **STATIC_ROOT:** `staticfiles/` (created by `collectstatic`).
- **Media (uploads):** Stored in `MEDIA_ROOT` (default `media/`). On PaaS, this is often ephemeral; for persistent uploads use a cloud storage backend (e.g. **AWS S3** with `django-storages` and `boto3`). Configure in settings and set `DEFAULT_FILE_STORAGE` and related env vars.

---

## 6. Database

- **Development:** SQLite is used when `DATABASE_URL` is not set.
- **Production:** Set `DATABASE_URL` to a **PostgreSQL** URL, e.g.:
  ```text
  postgres://USER:PASSWORD@HOST:5432/DATABASE
  ```
  Many hosts (Heroku, Render, Railway, etc.) set `DATABASE_URL` automatically when you add a PostgreSQL add-on.

After deployment or DB change:

```bash
python manage.py migrate
python manage.py createsuperuser  # if needed
```

---

## 7. Environment variables

Copy `.env.example` to `.env` (and do **not** commit `.env`). In production, set these in the hosting dashboard or CLI.

| Variable | Required in prod | Example |
|----------|-------------------|----------|
| `DJANGO_SECRET_KEY` | Yes | Long random string |
| `DJANGO_DEBUG` | Yes | `False` |
| `ALLOWED_HOSTS` | Yes | `api.yourdomain.com,yourdomain.com` |
| `DATABASE_URL` | Yes (for PostgreSQL) | `postgres://...` (often set by host) |
| `CSRF_TRUSTED_ORIGINS` | If using HTTPS | `https://api.yourdomain.com` |
| `SECURE_SSL_REDIRECT` | Optional | `True` |
| `LOG_TO_FILE` | Optional | `1` (ensure `logs/` exists) |
| `DJANGO_LOG_LEVEL` | Optional | `INFO` |

---

## 8. Deploy steps (generic)

1. **Push code** to your Git repository.
2. **Create the app** on your chosen platform and connect the repo.
3. **Add a PostgreSQL database** (if required) and ensure `DATABASE_URL` is set.
4. **Set environment variables** (see [§7](#7-environment-variables)).
5. **Build command** (if applicable):  
   `pip install -r requirements.txt && python manage.py collectstatic --noinput`
6. **Start command:**  
   Use the Procfile’s `web` command, or explicitly:  
   `gunicorn social_media_api.wsgi --bind 0.0.0.0:$PORT`
7. **Run migrations** (often via a release phase or one-off command):  
   `python manage.py migrate`
8. **Optional:** Create a superuser:  
   `python manage.py createsuperuser`

---

## 9. Platform-specific notes

### Heroku

- Add buildpack: `heroku/python`.
- Add PostgreSQL: `heroku addons:create heroku-postgresql:mini`.
- Config vars: set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, `ALLOWED_HOSTS` (include `yourapp.herokuapp.com`).
- Release phase (optional): add `release: python manage.py migrate` in Procfile or use Heroku release phase in `app.json` / dashboard.

### Render

- **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- **Start Command:** `gunicorn social_media_api.wsgi --bind 0.0.0.0:$PORT`
- Add a PostgreSQL database in the same group and use the provided `DATABASE_URL`.
- Set `ALLOWED_HOSTS` to include your Render hostname (e.g. `yourapp.onrender.com`).

### Railway

- Connect repo; Railway detects the Procfile.
- Add PostgreSQL from the dashboard; `DATABASE_URL` is set automatically.
- Set `ALLOWED_HOSTS` to include the Railway-generated domain.

### DigitalOcean App Platform

- Connect repo; use a similar build/start command as above.
- Add a PostgreSQL database component and map its connection string to `DATABASE_URL`.
- Set `ALLOWED_HOSTS` to your app’s URL.

---

## 10. Monitoring and maintenance

- **Logging:** The project configures console logging by default. Set `LOG_TO_FILE=1` and ensure a `logs/` directory exists if you want file logging.
- **Health:** Use a simple endpoint (e.g. `GET /api/` or a dedicated `/health/`) and point your platform’s health check at it.
- **Updates:** Periodically update dependencies (`pip install -u -r requirements.txt` and re-test), then redeploy.
- **Backups:** Use your host’s backup for the database (e.g. Heroku PG backups, Render/Railway backups). For media, use your storage provider’s backup if using S3.

---

## 11. Final testing

After deployment:

1. **Live URL:** Open the base URL (e.g. `https://yourapp.onrender.com/`) and confirm the API is reachable.
2. **Admin:** Visit `https://yourapp.../admin/` and log in with a superuser.
3. **API:** Test register, login, and a few endpoints (e.g. posts, feed) with token auth.
4. **HTTPS:** Confirm pages are served over HTTPS and that redirect from HTTP works if applicable.
5. **Static:** Load a page that uses static files (e.g. admin CSS) to confirm Whitenoise serves them.

---

## Deliverables checklist

- [x] **Deployment configuration:** `Procfile`, `runtime.txt`, `nginx.conf.example`, `.env.example`, `.gitignore`.
- [ ] **Live URL:** *(Fill in after deploy, e.g. https://social-media-api-xxxx.onrender.com)*
- [x] **Documentation:** This file (DEPLOYMENT.md) and references in README.

For day-to-day development and API usage, see the main **README.md**.
