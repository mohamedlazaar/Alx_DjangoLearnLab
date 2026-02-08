"""
Unit tests for the Book API endpoints.

Tests cover:
- CRUD operations (Create, Read, Update, Delete)
- Filtering by title, author, and publication_year
- Search and ordering
- Permissions and authentication
- Response data integrity and status codes
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Author, Book

User = get_user_model()


class BookAPITestCase(APITestCase):
    """Base test case with common setup for Book API tests."""

    def setUp(self):
        """Create test user, authors, and books for each test."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.author1 = Author.objects.create(name='Author One')
        self.author2 = Author.objects.create(name='Author Two')
        self.book1 = Book.objects.create(
            title='Python Programming',
            publication_year=2020,
            author=self.author1
        )
        self.book2 = Book.objects.create(
            title='Django for Beginners',
            publication_year=2022,
            author=self.author1
        )
        self.book3 = Book.objects.create(
            title='REST API Design',
            publication_year=2019,
            author=self.author2
        )


# --- List & Detail (Read) ---


class BookListTests(BookAPITestCase):
    """Tests for GET /books/ (list all books)."""

    def test_list_books_unauthenticated_returns_200(self):
        """Anonymous users can list books (AllowAny / IsAuthenticatedOrReadOnly)."""
        url = reverse('book-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_books_returns_correct_structure(self):
        """List response is a list of book objects with expected fields."""
        url = reverse('book-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 3)
        first = response.data[0]
        for key in ('id', 'title', 'publication_year', 'author', 'author_name'):
            self.assertIn(key, first)

    def test_list_books_data_integrity(self):
        """List response contains correct book data."""
        url = reverse('book-list')
        response = self.client.get(url)
        titles = [b['title'] for b in response.data]
        self.assertIn('Python Programming', titles)
        self.assertIn('Django for Beginners', titles)
        self.assertIn('REST API Design', titles)


class BookDetailTests(BookAPITestCase):
    """Tests for GET /books/<pk>/ (retrieve one book)."""

    def test_detail_books_unauthenticated_returns_200(self):
        """Anonymous users can retrieve a single book."""
        url = reverse('book-detail', kwargs={'pk': self.book1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_returns_correct_data(self):
        """Detail response contains correct book and author_name."""
        url = reverse('book-detail', kwargs={'pk': self.book1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.book1.pk)
        self.assertEqual(response.data['title'], 'Python Programming')
        self.assertEqual(response.data['publication_year'], 2020)
        self.assertEqual(response.data['author'], self.author1.pk)
        self.assertEqual(response.data['author_name'], 'Author One')

    def test_detail_invalid_pk_returns_404(self):
        """Requesting non-existent book returns 404."""
        url = reverse('book-detail', kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# --- Create ---


class BookCreateTests(BookAPITestCase):
    """Tests for POST /books/create/ (create book)."""

    def test_create_unauthenticated_returns_401(self):
        """Creating a book without auth returns 401."""
        url = reverse('book-create')
        data = {
            'title': 'New Book',
            'publication_year': 2023,
            'author': self.author1.pk,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_authenticated_returns_201_and_saves(self):
        """Authenticated user can create a book; data is saved and returned."""
        self.client.force_authenticate(user=self.user)
        url = reverse('book-create')
        data = {
            'title': 'New Book',
            'publication_year': 2023,
            'author': self.author1.pk,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['title'], 'New Book')
        self.assertEqual(response.data['data']['publication_year'], 2023)
        self.assertTrue(Book.objects.filter(title='New Book').exists())

    def test_create_invalid_publication_year_returns_400(self):
        """Publication year in the future is rejected with 400."""
        from datetime import datetime
        self.client.force_authenticate(user=self.user)
        url = reverse('book-create')
        future_year = datetime.now().year + 1
        data = {
            'title': 'Future Book',
            'publication_year': future_year,
            'author': self.author1.pk,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# --- Update ---


class BookUpdateTests(BookAPITestCase):
    """Tests for PUT/PATCH /books/<pk>/update/."""

    def test_update_unauthenticated_returns_401(self):
        """Updating without auth returns 401."""
        url = reverse('book-update', kwargs={'pk': self.book1.pk})
        data = {'title': 'Updated Title', 'publication_year': 2021, 'author': self.author1.pk}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_authenticated_put_returns_200_and_updates(self):
        """Authenticated PUT updates book and returns 200 with message and data."""
        self.client.force_authenticate(user=self.user)
        url = reverse('book-update', kwargs={'pk': self.book1.pk})
        data = {
            'title': 'Updated Title',
            'publication_year': 2021,
            'author': self.author1.pk,
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['title'], 'Updated Title')
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'Updated Title')
        self.assertEqual(self.book1.publication_year, 2021)

    def test_update_authenticated_patch_partial(self):
        """Authenticated PATCH can update only some fields."""
        self.client.force_authenticate(user=self.user)
        url = reverse('book-update', kwargs={'pk': self.book1.pk})
        response = self.client.patch(url, {'title': 'Patched Title'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'Patched Title')


# --- Delete ---


class BookDeleteTests(BookAPITestCase):
    """Tests for DELETE /books/<pk>/delete/."""

    def test_delete_unauthenticated_returns_401(self):
        """Deleting without auth returns 401."""
        url = reverse('book-delete', kwargs={'pk': self.book1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_authenticated_returns_204_and_removes_book(self):
        """Authenticated delete returns 204 and removes the book."""
        self.client.force_authenticate(user=self.user)
        pk = self.book1.pk
        url = reverse('book-delete', kwargs={'pk': pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(pk=pk).exists())


# --- Filtering, Search, Ordering ---


class BookFilteringTests(BookAPITestCase):
    """Tests for filtering by title, author, publication_year."""

    def test_filter_by_title(self):
        """Filtering by title returns matching books."""
        url = reverse('book-list')
        response = self.client.get(url, {'title': 'Python Programming'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Python Programming')

    def test_filter_by_author(self):
        """Filtering by author id returns books by that author."""
        url = reverse('book-list')
        response = self.client.get(url, {'author': self.author1.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for item in response.data:
            self.assertEqual(item['author'], self.author1.pk)

    def test_filter_by_publication_year(self):
        """Filtering by publication_year returns matching books."""
        url = reverse('book-list')
        response = self.client.get(url, {'publication_year': 2022})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['publication_year'], 2022)


class BookSearchTests(BookAPITestCase):
    """Tests for search on title and author name."""

    def test_search_by_title(self):
        """Search matches title (partial)."""
        url = reverse('book-list')
        response = self.client.get(url, {'search': 'Django'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertIn('Django', response.data[0]['title'])

    def test_search_by_author_name(self):
        """Search matches author name."""
        url = reverse('book-list')
        response = self.client.get(url, {'search': 'Author Two'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['author_name'], 'Author Two')


class BookOrderingTests(BookAPITestCase):
    """Tests for ordering by title, publication_year, author__name."""

    def test_ordering_by_title_asc(self):
        """Order by title returns books in title order."""
        url = reverse('book-list')
        response = self.client.get(url, {'ordering': 'title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [b['title'] for b in response.data]
        self.assertEqual(titles, sorted(titles))

    def test_ordering_by_title_desc(self):
        """Order by -title returns books in reverse title order."""
        url = reverse('book-list')
        response = self.client.get(url, {'ordering': '-title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [b['title'] for b in response.data]
        self.assertEqual(titles, sorted(titles, reverse=True))

    def test_ordering_by_publication_year(self):
        """Order by publication_year works."""
        url = reverse('book-list')
        response = self.client.get(url, {'ordering': 'publication_year'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        years = [b['publication_year'] for b in response.data]
        self.assertEqual(years, sorted(years))


# --- Permissions (read vs write) ---


class BookPermissionTests(BookAPITestCase):
    """Tests for permission enforcement on read vs write endpoints."""

    def test_list_allowed_without_auth(self):
        """List is readable without authentication."""
        response = self.client.get(reverse('book-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_allowed_without_auth(self):
        """Detail is readable without authentication."""
        response = self.client.get(reverse('book-detail', kwargs={'pk': self.book1.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_requires_auth(self):
        """Create requires authentication."""
        response = self.client.post(reverse('book-create'), {
            'title': 'X', 'publication_year': 2020, 'author': self.author1.pk
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_requires_auth(self):
        """Update requires authentication."""
        response = self.client.put(
            reverse('book-update', kwargs={'pk': self.book1.pk}),
            {'title': 'X', 'publication_year': 2020, 'author': self.author1.pk},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_requires_auth(self):
        """Delete requires authentication."""
        response = self.client.delete(reverse('book-delete', kwargs={'pk': self.book1.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
