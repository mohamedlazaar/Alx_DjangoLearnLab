from django.urls import path
from . import views

"""
API URL Configuration for Book Management

Routes:
- GET    /api/books/                 - List all books
- GET    /api/books/<int:pk>/        - Retrieve a specific book
- POST   /api/books/create/          - Create a new book (authenticated)
- PUT    /api/books/<int:pk>/update/ - Update a book (authenticated)
- PATCH  /api/books/<int:pk>/update/ - Partial update (authenticated)
- DELETE /api/books/<int:pk>/delete/ - Delete a book (authenticated)
- GET    /api/authors/               - List all authors with books
- GET    /api/authors/<int:pk>/      - Retrieve a specific author

Permissions:
- Read operations (GET): No authentication required
- Write operations (POST, PUT, PATCH, DELETE): Authentication required
"""

urlpatterns = [
    # Book CRUD endpoints
    path('books/', views.ListView.as_view(), name='book-list'),
    path('books/<int:pk>/', views.DetailView.as_view(), name='book-detail'),
    path('books/create/', views.CreateView.as_view(), name='book-create'),
    path('books/<int:pk>/update/', views.UpdateView.as_view(), name='book-update'),
    path('books/<int:pk>/delete/', views.DeleteView.as_view(), name='book-delete'),
]