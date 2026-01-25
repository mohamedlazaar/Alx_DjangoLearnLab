# Delete Operation


**Command:**

from bookshelf.models import Book
new_book = Book.objects.get(title="Nineteen Eighty-Four")
new_book.delete()

#Output
(1, {'bookshelf.Book': 1})

all_books = Book.objects.all()
>>> print(all_books)

#Output
<QuerySet []>