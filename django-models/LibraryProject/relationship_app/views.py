from django.shortcuts import render
from django.views.generic import DetailView, ListView
from .models import  Library, Book, Librarian, Author

# Create your views here.

# Function-based view: List all books
def list_books(request):
    books = Book.objects.all()
    return render(request, 'relationship_app/list_books.html', {'books': books})

# Class-based view: Show details of a specific library
class LibraryDetailView(DetailView):
    model = Library
    template_name = 'relationship_app/library_detail.html'
    context_object_name = 'library'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['books'] = self.object.books.all()
    #     return context