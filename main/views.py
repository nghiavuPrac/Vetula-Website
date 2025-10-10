from django.shortcuts import render, get_object_or_404
from .models import Recipe
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from . import api_config
from py_edamam import Edamam
import json


ed_handler = Edamam(recipes_appid=api_config.recipes_appid,
                recipes_appkey=api_config.recipes_appkey)

class Food_Recipe():
    def __init__(self,data):
        self.title = data["label"]
        self.image = data["image"]
        self.description = data["healthLabels"]
        self.url = data["url"]
        self.time = data["totalTime"]
        self.calories = data["calories"]
        self.fat = data["totalNutrients"]["FAT"]['quantity']
        self.protein = data["totalNutrients"]['PROCNT']['quantity']
        self.carbs = data["totalNutrients"]['CHOCDF']['quantity']
        self.cusine = data["cuisineType"]

    def save(self):
        pass
    def describe(self):
        return " * ".join(self.description)


def proccess_data(data):
    try:
        payload = data["hits"]
        results= [Food_Recipe(item["recipe"]) for item in payload]
        total = data["count"]
    except:
        results = list()
        total = 0

    return results, total


def search_with_API(request):
    topic = "Edamam"
    query = request.GET.get("search")
    results = list()
    total = 0

    # Check if the query is the same as the one in the session
    if request.session.get("query") == query and "data" in request.session:
        data = request.session["data"]
        results, total = proccess_data(data)
    else:
        # If query is new or missing, make a new API call
        if query:
            try:
                data = ed_handler.search_recipe(query)
                results, total = proccess_data(data)
                # Update the session
                request.session["query"] = query
                request.session["data"] = data
            except Exception:
                results, total = [], 0
        else:
            # Handle case where search is initiated without a query
            results, total = [], 0

    #paginate results
    paginator = Paginator(results, 3)
    page = request.GET.get("page")
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)

    context = {
        "topic":topic,
        "page":page,
        "total":total,
        "query":query,
        "results":results,
    }
    return render(request, "search.html", context)




def home(request):
    total_recipes = Recipe.objects.all().count()
    context = {
        "title":"Homepage",
        "total_recipes":total_recipes,
    }

    return render(request, "home.html", context)



def search(request):
    recipes = Recipe.objects.all().order_by('pk')
    query = request.GET.get("search", "")

    if query:
        queryset = recipes.filter(Q(title__icontains=query))
    else:
        queryset = recipes

    results = queryset
    topic = ""

    topic_map = {
        "breakfast": "breakfast",
        "appetizers": "appetizers",
        "lunch": "lunch",
        "salads": "salads",
        "dinner": "dinner",
        "dessert": "dessert",
        "easy": "easy",
        "hard": "hard"
    }

    for key, value in topic_map.items():
        if request.GET.get(key):
            results = queryset.filter(Q(topic__title__icontains=value))
            topic = value
            break  # Process only the first topic found

    total = results.count()

    #paginate results
    paginator = Paginator(results, 3)
    page = request.GET.get("page")
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)

    context = {
        "topic":topic,
        "page":page,
        "total":total,
        "query":query,
        "results":results,
    }
    return render(request, "search.html", context)

def detail(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug)
    context = {
        "recipe":recipe,
    }
    return render(request, "detail.html", context)