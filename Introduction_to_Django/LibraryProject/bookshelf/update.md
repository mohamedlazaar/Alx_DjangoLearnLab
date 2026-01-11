# Update Operation

**Command:** 


new_book = Book.objects.get(title="1984")
new_book.title = "Nineteen Eighty-Four"
new_book.save()
print(new_book.title)

#Output
Nineteen Eighty-Four