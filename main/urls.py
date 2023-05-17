from django.urls import path
from .views import home, search, detail, search_with_API

urlpatterns = [
    path("", home, name="home"),
    #path("search", search, name="search"),
    path("search", search_with_API, name="search"),
    path("<slug>", detail, name="detail"),
]