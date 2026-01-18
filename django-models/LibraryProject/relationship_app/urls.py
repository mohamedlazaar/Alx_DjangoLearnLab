from django.urls import path
from . import views

urlpatterns = [
    path("list", views.ListView, name="list"),
    path("detail", views.DetailView, name="detail"),
]