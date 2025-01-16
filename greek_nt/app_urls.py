# greek_nt/app_urls.py
from django.urls import path
from . import views

app_name = "greek_nt"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("search/", views.SearchView.as_view(), name="search"),
]
