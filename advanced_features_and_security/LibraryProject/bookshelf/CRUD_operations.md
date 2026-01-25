# Create Operation

**Command:**

from bookshelf.models import Book
new_book = Book.objects.create(title="1984", author="George Orwell", publication_year=1949)
print(new_book)

#Output
Book object (1)

# Retrieve Operation

**Command:**
```python
from bookshelf.models import Book
new_book = Book.objects.get(title="1984")
print(f"Title: {new_book.title}, Author: {new_book.author}, Year: {new_book.publication_year}")

#Output
Title: 1984, Author: George Orwell, Year: 1949

# Update Operation

**Command:**
```python
new_book = Book.objects.get(title="1984")
new_book.title = "Nineteen Eighty-Four"
new_book.save()
print(new_book.title)

#Output
Nineteen Eighty-Four

# Delete Operation

**Command:**
```python
new_book = Book.objects.get(title="Nineteen Eighty-Four")
new_book.delete()

#Output
(1, {'bookshelf.Book': 1})

all_books = Book.objects.all()
>>> print(all_books)

#Output
<QuerySet []>