from rest_framework import serializers
from .models import Book, Author
from datetime import datetime


class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for the Book model.
    
    Features:
    - Serializes all Book fields (id, title, publication_year, author)
    - Includes author_name as a read-only field for convenience
    - Custom validation: publication_year cannot be in the future
    """
    author_name = serializers.CharField(source='author.name', read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'publication_year', 'author', 'author_name']

    def validate_publication_year(self, value):
        """
        Validate that publication_year is not in the future.
        
        Args:
            value: The publication_year value to validate
            
        Raises:
            ValidationError: If publication_year is greater than current year
        """
        current_year = datetime.now().year
        if value > current_year:
            raise serializers.ValidationError(
                f"Publication year cannot be in the future. Current year is {current_year}."
            )
        return value

    def validate(self, data):
        """
        Additional validation at the object level (if needed).
        """
        return data


class AuthorSerializer(serializers.ModelSerializer):
    """
    Serializer for the Author model.
    
    Features:
    - Serializes author name
    - Includes nested BookSerializer for all related books
    - Provides complete author information with their book collection
    """
    books = BookSerializer(many=True, read_only=True)

    class Meta:
        model = Author
        fields = ['id', 'name', 'books']
