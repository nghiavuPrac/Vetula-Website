from django.urls import path
from .views import home, search, detail, search_with_API

app_name = "main"

urlpatterns = [
    path("", home, name="home"),
    # path("search/", search, name="search"),
    path("search/", search_with_API, name="search"),
    path("detail/<slug:slug>/", detail, name="detail"),
]