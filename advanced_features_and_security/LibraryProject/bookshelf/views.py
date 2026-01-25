from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
# from .forms import ExampleForm
from django.http import HttpResponse
from django.shortcuts import render


# def form_example(request):
#     form = ExampleForm()
#     return render(request, "bookshelf/form_example.html", {"form": form})



# @csrf_protect
# def secure_view(request):
#     response = HttpResponse("Secure content")
#     response["Content-Security-Policy"] = "default-src 'self'"
#     return response

# Permission-based book views

@permission_required('bookshelf.can_view', raise_exception=True)
def book_list(request):
    return HttpResponse("List of books")


@permission_required('bookshelf.can_create', raise_exception=True)
def create_book(request):
    return HttpResponse("Create book")


@permission_required('bookshelf.can_edit', raise_exception=True)
def edit_book(request):
    return HttpResponse("Edit book")


@permission_required('bookshelf.can_delete', raise_exception=True)
def delete_book(request):
    return HttpResponse("Delete book")