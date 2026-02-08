# API Views Configuration Documentation

## Overview
This document provides detailed information about the DRF generic views implemented for Book management, including CRUD operations, permissions, and usage examples.

---

## Table of Contents
1. [Views Overview](#views-overview)
2. [URL Patterns](#url-patterns)
3. [Permissions](#permissions)
4. [View Details](#view-details)
5. [Testing Examples](#testing-examples)
6. [Error Handling](#error-handling)

---

## Views Overview

### CRUD Views for Books

| View | HTTP Method | URL | Purpose | Permissions |
|------|-------------|-----|---------|-------------|
| `ListView` | GET | `/api/books/` | List all books | AllowAny |
| `DetailView` | GET | `/api/books/<id>/` | Get single book | AllowAny |
| `CreateView` | POST | `/api/books/create/` | Create new book | IsAuthenticated |
| `UpdateView` | PUT/PATCH | `/api/books/<id>/update/` | Update book | IsAuthenticated |
| `DeleteView` | DELETE | `/api/books/<id>/delete/` | Delete book | IsAuthenticated |

### Author Views

| View | HTTP Method | URL | Purpose | Permissions |
|------|-------------|-----|---------|-------------|
| `AuthorListView` | GET | `/api/authors/` | List all authors | AllowAny |
| `AuthorDetailView` | GET | `/api/authors/<id>/` | Get author with books | AllowAny |

---

## URL Patterns

```python
# Book endpoints
GET    /api/books/                   # List all books
GET    /api/books/<int:pk>/          # Retrieve specific book
POST   /api/books/create/            # Create new book
PUT    /api/books/<int:pk>/update/   # Full update
PATCH  /api/books/<int:pk>/update/   # Partial update
DELETE /api/books/<int:pk>/delete/   # Delete book

# Author endpoints
GET    /api/authors/                 # List all authors
GET    /api/authors/<int:pk>/        # Retrieve specific author
```

---

## Permissions

### Permission Classes Used

1. **AllowAny**
   - Read-only endpoints (List, Detail)
   - No authentication required
   - Used for: `ListView`, `DetailView`, `AuthorListView`, `AuthorDetailView`

2. **IsAuthenticated**
   - Write operations (Create, Update, Delete)
   - User must provide valid token or session
   - Used for: `CreateView`, `UpdateView`, `DeleteView`

### Permission Inheritance

All views inherit from DRF's generic views:
- `ListAPIView` - Read-only list
- `RetrieveAPIView` - Read-only detail
- `CreateAPIView` - Create only
- `UpdateAPIView` - Update only (supports PUT and PATCH)
- `DestroyAPIView` - Delete only

---

## View Details

### 1. ListView - Retrieve All Books

**Configuration:**
```python
class ListView(generics.ListAPIView):
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
```

**Features:**
- Returns list of all books
- Uses `select_related('author')` for query optimization
- No pagination configured (can be added in settings)

**Request:**
```bash
GET /api/books/
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "The Great Gatsby",
    "publication_year": 1925,
    "author": 1,
    "author_name": "F. Scott Fitzgerald"
  },
  {
    "id": 2,
    "title": "1984",
    "publication_year": 1949,
    "author": 2,
    "author_name": "George Orwell"
  }
]
```

---

### 2. DetailView - Retrieve Single Book

**Configuration:**
```python
class DetailView(generics.RetrieveAPIView):
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
```

**Features:**
- Returns details for a specific book
- Looks up by primary key (pk)

**Request:**
```bash
GET /api/books/1/
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "The Great Gatsby",
  "publication_year": 1925,
  "author": 1,
  "author_name": "F. Scott Fitzgerald"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

---

### 3. CreateView - Create New Book

**Configuration:**
```python
class CreateView(generics.CreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
```

**Features:**
- Requires authentication
- Validates data using BookSerializer
- Custom validation: publication_year cannot be in future
- Returns created object with ID

**Custom Methods:**
```python
def perform_create(self, serializer):
    """Called after validation, before save."""
    serializer.save()

def create(self, request, *args, **kwargs):
    """Customized response format."""
    response = super().create(request, *args, **kwargs)
    return Response(
        {"message": "Book created successfully", "data": response.data},
        status=status.HTTP_201_CREATED
    )
```

**Request:**
```bash
POST /api/books/create/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{
  "title": "New Book",
  "publication_year": 2025,
  "author": 1
}
```

**Response (201 Created):**
```json
{
  "message": "Book created successfully",
  "data": {
    "id": 3,
    "title": "New Book",
    "publication_year": 2025,
    "author": 1,
    "author_name": "Author Name"
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "publication_year": [
    "Publication year cannot be in the future. Current year is 2026."
  ]
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

### 4. UpdateView - Update Book

**Configuration:**
```python
class UpdateView(generics.UpdateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
```

**Features:**
- Supports both PUT (full update) and PATCH (partial update)
- Requires authentication
- Same validation as CreateView

**Custom Methods:**
```python
def perform_update(self, serializer):
    """Called after validation, before save."""
    serializer.save()

def update(self, request, *args, **kwargs):
    """Customized response format."""
    response = super().update(request, *args, **kwargs)
    return Response(
        {"message": "Book updated successfully", "data": response.data},
        status=status.HTTP_200_OK
    )
```

**Full Update (PUT):**
```bash
PUT /api/books/1/update/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{
  "title": "Updated Title",
  "publication_year": 2025,
  "author": 1
}
```

**Partial Update (PATCH):**
```bash
PATCH /api/books/1/update/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{
  "title": "Updated Title Only"
}
```

**Response (200 OK):**
```json
{
  "message": "Book updated successfully",
  "data": {
    "id": 1,
    "title": "Updated Title",
    "publication_year": 2025,
    "author": 1,
    "author_name": "Author Name"
  }
}
```

---

### 5. DeleteView - Delete Book

**Configuration:**
```python
class DeleteView(generics.DestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
```

**Features:**
- Requires authentication
- Returns custom deletion message
- Returns 204 No Content on success

**Custom Method:**
```python
def destroy(self, request, *args, **kwargs):
    """Override to provide custom response."""
    instance = self.get_object()
    book_title = instance.title
    self.perform_destroy(instance)
    return Response(
        {"message": f"Book '{book_title}' deleted successfully"},
        status=status.HTTP_204_NO_CONTENT
    )
```

**Request:**
```bash
DELETE /api/books/1/delete/
Authorization: Token YOUR_TOKEN
```

**Response (204 No Content):**
```json
{
  "message": "Book 'Book Title' deleted successfully"
}
```

---

### 6. Author Views

#### AuthorListView
```bash
GET /api/authors/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "F. Scott Fitzgerald",
    "books": [
      {
        "id": 1,
        "title": "The Great Gatsby",
        "publication_year": 1925,
        "author": 1,
        "author_name": "F. Scott Fitzgerald"
      }
    ]
  }
]
```

#### AuthorDetailView
```bash
GET /api/authors/1/
```

**Response:**
```json
{
  "id": 1,
  "name": "F. Scott Fitzgerald",
  "books": [
    {
      "id": 1,
      "title": "The Great Gatsby",
      "publication_year": 1925,
      "author": 1,
      "author_name": "F. Scott Fitzgerald"
    }
  ]
}
```

---

## Testing Examples

### Using cURL

**1. List Books (No Auth):**
```bash
curl http://127.0.0.1:8000/api/books/
```

**2. Get Single Book (No Auth):**
```bash
curl http://127.0.0.1:8000/api/books/1/
```

**3. Create Book (With Auth):**
```bash
curl -X POST http://127.0.0.1:8000/api/books/create/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Book",
    "publication_year": 2025,
    "author": 1
  }'
```

**4. Update Book (With Auth):**
```bash
curl -X PATCH http://127.0.0.1:8000/api/books/1/update/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'
```

**5. Delete Book (With Auth):**
```bash
curl -X DELETE http://127.0.0.1:8000/api/books/1/delete/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Using Postman

1. **Create Collection** named "Book API"
2. **Set up environment variables:**
   - `base_url`: `http://127.0.0.1:8000/api`
   - `token`: `YOUR_TOKEN_HERE`

3. **Create requests:**
   - GET `/books/` - Authorization: None
   - POST `/books/create/` - Authorization: Bearer Token
   - PATCH `/books/{{book_id}}/update/` - Authorization: Bearer Token
   - DELETE `/books/{{book_id}}/delete/` - Authorization: Bearer Token

---

## Error Handling

### Common HTTP Status Codes

| Status | Meaning | Example |
|--------|---------|---------|
| 200 | OK | Successful GET, PATCH, PUT |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 405 | Method Not Allowed | Wrong HTTP method |
| 500 | Server Error | Internal server error |

### Validation Error Example

**Request:**
```json
{
  "title": "Book",
  "publication_year": 2030,
  "author": 1
}
```

**Response (400 Bad Request):**
```json
{
  "publication_year": [
    "Publication year cannot be in the future. Current year is 2026."
  ]
}
```

### Authentication Error

**Response (401 Unauthorized):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Response (Invalid Token):**
```json
{
  "detail": "Invalid token."
}
```

---

## Query Optimization

### Database Queries

Views use `.select_related()` and `.prefetch_related()` for optimization:

```python
# ListView & DetailView - Single query with author data
queryset = Book.objects.all().select_related('author')

# AuthorListView & AuthorDetailView - Prefetch related books
queryset = Author.objects.prefetch_related('books')
```

### Pagination (Optional Enhancement)

To add pagination, update `settings.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}
```

---

## Summary

- **Read Operations**: No authentication required, optimized queries
- **Write Operations**: Authentication required, validated data
- **Custom Responses**: Enhanced messages for better UX
- **Error Handling**: Detailed error messages for debugging
- **Query Optimization**: Uses select_related/prefetch_related

For more information, refer to:
- [DRF Generic Views Documentation](https://www.django-rest-framework.org/api-guide/generic-views/)
- [DRF Permissions Documentation](https://www.django-rest-framework.org/api-guide/permissions/)

