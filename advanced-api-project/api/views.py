from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from .models import Book, Author
from .serializers import BookSerializer

"""
API Views for Book Management

This module provides a complete set of generic views for CRUD operations on the Book model.
Each view is configured with appropriate permissions and serializers.

Permissions:
- ListView & DetailView: AllowAny (read-only access)
- CreateView, UpdateView, DeleteView: IsAuthenticated (authenticated users only)

Serialization: Uses BookSerializer for proper data validation and representation.
"""


class ListView(generics.ListAPIView):
    """
    List all books.
    
    HTTP Method: GET
    URL: /api/books/
    Permissions: AllowAny (no authentication required)
    
    Returns:
        200 OK: List of all books with their details
        
    Example:
        GET /api/books/
        Response: [{"id": 1, "title": "Book 1", ...}, ...]
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]


class DetailView(generics.RetrieveAPIView):
    """
    Retrieve a single book by ID.
    
    HTTP Method: GET
    URL: /api/books/<int:pk>/
    Permissions: AllowAny (no authentication required)
    
    Parameters:
        pk (int): Primary key of the book to retrieve
        
    Returns:
        200 OK: Book details including author information
        404 Not Found: If book does not exist
        
    Example:
        GET /api/books/1/
        Response: {"id": 1, "title": "Book Title", "author": 1, ...}
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]


class CreateView(generics.CreateAPIView):
    """
    Create a new book.
    
    HTTP Method: POST
    URL: /api/books/create/
    Permissions: IsAuthenticated (authenticated users only)
    
    Request Body:
        {
            "title": "string",
            "publication_year": integer,
            "author": integer (author ID)
        }
        
    Returns:
        201 Created: Newly created book object
        400 Bad Request: Invalid data or validation errors
        401 Unauthorized: If not authenticated
        
    Validation:
        - title: Required, max 200 characters
        - publication_year: Required, must not be in future
        - author: Required, must be valid author ID
        
    Example:
        POST /api/books/create/
        Body: {"title": "New Book", "publication_year": 2025, "author": 1}
        Response: {"id": 2, "title": "New Book", ...}
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        """
        Handle custom logic after book creation.
        
        This method is called after validation passes but before saving to database.
        Can be overridden to add additional logic like logging or notifications.
        """
        serializer.save()
    
    def create(self, request, *args, **kwargs):
        """
        Override create to provide custom response handling.
        """
        response = super().create(request, *args, **kwargs)
        return Response(
            {"message": "Book created successfully", "data": response.data},
            status=status.HTTP_201_CREATED
        )


class UpdateView(generics.UpdateAPIView):
    """
    Update an existing book.
    
    HTTP Method: PUT or PATCH
    URL: /api/books/<int:pk>/update/
    Permissions: IsAuthenticated (authenticated users only)
    
    Parameters:
        pk (int): Primary key of the book to update
        
    Request Body (PUT - all fields required):
        {
            "title": "string",
            "publication_year": integer,
            "author": integer
        }
        
    Request Body (PATCH - only fields to update):
        {
            "title": "Updated Title"
        }
        
    Returns:
        200 OK: Updated book object
        400 Bad Request: Invalid data or validation errors
        401 Unauthorized: If not authenticated
        404 Not Found: If book does not exist
        
    Examples:
        PUT /api/books/1/update/
        Body: {"title": "Updated Title", "publication_year": 2025, "author": 1}
        Response: {"id": 1, "title": "Updated Title", ...}
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_update(self, serializer):
        """Handle custom logic after book update."""
        serializer.save()
    
    def update(self, request, *args, **kwargs):
        """Override update to provide custom response handling."""
        response = super().update(request, *args, **kwargs)
        return Response(
            {"message": "Book updated successfully", "data": response.data},
            status=status.HTTP_200_OK
        )


class DeleteView(generics.DestroyAPIView):
    """
    Delete an existing book.
    
    HTTP Method: DELETE
    URL: /api/books/<int:pk>/delete/
    Permissions: IsAuthenticated (authenticated users only)
    
    Parameters:
        pk (int): Primary key of the book to delete
        
    Returns:
        204 No Content: Successful deletion
        401 Unauthorized: If not authenticated
        404 Not Found: If book does not exist
        
    Example:
        DELETE /api/books/1/delete/
        Response: 204 No Content
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def destroy(self, request, *args, **kwargs):
        """Override destroy to provide custom response handling."""
        instance = self.get_object()
        book_title = instance.title
        self.perform_destroy(instance)
        return Response(
            {"message": f"Book '{book_title}' deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )





