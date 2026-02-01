from django.shortcuts import render
from .models import Book
from rest_framework import generics, viewsets, permissions
from .serializers import BookSerializer

"""
API Views with Token Authentication and Permission Classes

This module provides API endpoints for managing books with token-based 
authentication and role-based access control.

Authentication: Token-based (Authorization: Token <token>)
Default Permission: IsAuthenticated (all users must be logged in)
"""

class BookList(generics.ListAPIView):
    """
    List all books with token authentication.
    
    Permissions:
    - IsAuthenticated: User must provide a valid token
    
    Methods:
    - GET: Retrieve list of all books
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    
class BookViewSet(viewsets.ModelViewSet):
    """
    Complete CRUD operations for Book model with token authentication.
    
    Permissions:
    - IsAuthenticated: User must provide a valid token to access any endpoint
    
    Methods:
    - GET: Retrieve book(s)
    - POST: Create a new book (admin/staff only)
    - PUT: Update a book (admin/staff only)
    - PATCH: Partially update a book (admin/staff only)
    - DELETE: Delete a book (admin/staff only)
    
    Note: Write operations (POST, PUT, PATCH, DELETE) require admin/staff status
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]