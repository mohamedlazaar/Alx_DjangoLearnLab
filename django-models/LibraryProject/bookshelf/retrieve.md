# Retrieve Operation

## Command:



from bookshelf.models import Book
new_book = Book.objects.get(title="1984")
print(f"Title: {new_book.title}, Author: {new_book.author}, Year: {new_book.publication_year}")

#Output
Title: 1984, Author: George Orwell, Year: 1949