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
    if "query" in request.session:
        #if query in session load data from session 
        if query in request.session["query"] :
            data = request.session["data"]
            results, total = proccess_data(data)
        else:
            request.session.flush()
            data = ed_handler.search_recipe(query)
            results, total = proccess_data(data)  
            request.session["query"] = query
            request.session["data"] = data
    
    else:
        data = ed_handler.search_recipe(query)
        results, total = proccess_data(data)
        request.session["query"] = query
        request.session["data"] = data

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
    recipes = Recipe.objects.all()

    if "search" in request.GET:
        query = request.GET.get("search")
        queryset = recipes.filter(Q(title__icontains=query))
    if request.GET.get("breakfast"):
        results = queryset.filter(Q(topic__title__icontains="breakfast"))
        topic = "breakfast"
    elif request.GET.get("appetizers"):
        results = queryset.filter(Q(topic__title__icontains="appetizers"))
        topic="appetizers"
    elif request.GET.get("lunch"):
        results = queryset.filter(Q(topic__title__icontains="lunch"))
        topic="lunch"
    elif request.GET.get("salads"):
        results = queryset.filter(Q(topic__title__icontains="salads"))
        topic="salads"
    elif request.GET.get("dinner"):
        results = queryset.filter(Q(topic__title__icontains="dinner"))
        topic="dinner"
    elif request.GET.get("dessert"):
        results = queryset.filter(Q(topic__title__icontains="dessert"))
        topic="dessert"
    elif request.GET.get("easy"):
        results = queryset.filter(Q(topic__title__icontains="easy"))
        topic="easy"
    elif request.GET.get("hard"):
        results = queryset.filter(Q(topic__title__icontains="hard"))
        topic="hard"

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