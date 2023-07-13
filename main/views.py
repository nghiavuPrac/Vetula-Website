import logging
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

import uuid

from .forms import  ProfileForm, RecipeForm,form_validation_error

from .models import DB_Recipe, API_Recipe, Profile
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.conf import settings
# from py_edamam import Edamam

#import food_extraction
import subprocess as sp
import json
import os
import requests

from paypal.standard.forms import PayPalPaymentsForm
from django.views.decorators.csrf import csrf_exempt



# ed_handler = Edamam(recipes_appid=api_config.recipes_appid,
#                  recipes_appkey=api_config.recipes_appkey)    
app_id = settings.EDAMAM_ID
app_key = settings.EDAMAM_KEY
MAX_RECIPE_FREE = 5

class Edamam:
    def __init__(self,app_id, app_key, startPagination=0, endPagination=12):
        self.includeAppId = "app_id={}".format(app_id)
        self.includeAppKey = "app_key={}".format(app_key)
        self.startPagination = startPagination
        self.endPagination = endPagination

    def search_by_ingredients(self,inputIngredient):
        curl = f"https://api.edamam.com/search?q={inputIngredient}&{self.includeAppId}&{self.includeAppKey}&from={self.startPagination}&to={self.endPagination}"
        response = requests.get(curl)
        return response.json()

    def search_recipe(self,inputIngredient,inputCuisineType):
        curl = f"https://api.edamam.com/search?q={inputIngredient}&cuisineType={inputCuisineType}&{self.includeAppId}&{self.includeAppKey}&from={self.startPagination}&to={self.endPagination}"
        response = requests.get(curl)
        return response.json()

CuisineType_array = ["american", "british", "caribbean", 
                     "chinese", "french", "italian", 
                     "japanese", "kosher",
                     "mediterranean", "mexican"]


# utils
def get_topic(request):
    if request.GET.get("american"):
        topic = "american"
    elif request.GET.get("british"):
        topic="british"
    elif request.GET.get("caribbean"):
        topic="caribbean"
    elif request.GET.get("chinese"):
        topic="chinese"
    elif request.GET.get("french"):
        topic="french"
    elif request.GET.get("italian"):
        topic="italian"
    elif request.GET.get("japanese"):
        topic="japanese"
    elif request.GET.get("kosher"):
        topic="kosher"
    elif request.GET.get("mediterranean"):
        topic="mediterranean"
    elif request.GET.get("mexican"):
        topic="mexican"
    else:
        topic = "all"
    return topic

def proccess_query(data):
    try:
        payload = data["hits"]
        results= [API_Recipe(item["recipe"],index) for index,item in enumerate(payload)]
        total = data["count"]
    except:
        results = list()
        total = 0

    return results, total

def food_extraction(raw):
    extracted = sp.getoutput(f"python main/food_extraction/Ner.py \"{raw}\"")
    return extracted

# home page
def home(request):
    return render(request, "home.html")


# logic search and display
def search_API(request):
    query = request.GET.get("search")
    topic = get_topic(request)
    results = list()
    total = 0

    if query == "":
        results = list()
        extracted= ''
        total = 0

    else:
        if topic == "all":#search by ingredients only

            if "extracted" in request.session:
                #if query in session load data from session
                extracted = request.session["extracted"]
                if query == extracted:
                    data = request.session["data"]
                    results, total = proccess_query(data)
                else:
                #reset query
                    # request.session.clear()
                    print(request.user)
                    extracted = food_extraction(query)
                    api_handler = Edamam(app_id,app_key)
                    data = api_handler.search_by_ingredients(extracted)
                    results, total = proccess_query(data)  
                    request.session["data"] = data
                    request.session["extracted"]=extracted
            
            else:
            #initialize new query
                extracted = food_extraction(query)    
                api_handler = Edamam(app_id,app_key)
                data = api_handler.search_by_ingredients(query)
                results, total = proccess_query(data)
                request.session["data"] = data
                request.session["extracted"]=extracted

        else:#search by ingredients and cusine type
            if "extracted" in request.session and "topic" in request.session:
                #if query in session load data from session
                extracted = request.session["extracted"] 
                if (query==extracted) and topic in request.session["topic"]:
                    data = request.session["data"]
                    results, total = proccess_query(data)            
                else:
                    # request.session.clear()
                    extracted = food_extraction(query)
                    api_handler = Edamam(app_id,app_key)
                    data = api_handler.search_recipe(extracted,topic)
                    results, total = proccess_query(data)  
                    request.session["topic"] = topic
                    request.session["data"] = data
                    request.session["extracted"]=extracted
                    
            else:
                extracted = food_extraction(query)
                api_handler = Edamam(app_id,app_key)
                data = api_handler.search_recipe(extracted,topic)
                results, total = proccess_query(data)
                request.session["topic"] = topic
                request.session["data"] = data
                request.session["extracted"]=extracted
    

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
        "query":extracted,
        "results":results,
    }
    return render(request, "search.html", context)


def save_recipe(user,recipe):
    try:
        DB_Recipe.objects.get(title=recipe.title,user=user)
        return False,"The Recipe was saved"
    except:
        try:
            DB_Recipe(title= recipe.title,
                    image = recipe.image,
                    description= recipe.description,
                    ingredients= recipe.ingredients,
                    directions = recipe.directions,
                    servings = recipe.servings,
                    time = recipe.time,
                    calories = recipe.calories,
                    fat = recipe.fat,
                    carbs = recipe.carbs,
                    protein = recipe.protein,
                    topic = recipe.topic,
                    user = user).save()
            return True,"Save Success!"
        except:
           return False,"Fail to save!"

@login_required(login_url='login',redirect_field_name="next")
def recipe_detail(request,index):
    data = request.session["data"]
    payload = data["hits"]
    recipe = API_Recipe(payload[int(index)]["recipe"],index)

    if request.GET.get("save"):
        user = request.user.profile
        numRecipe = DB_Recipe.objects.filter(user=user).count()
        if request.user.profile.purchase:
            result,mess= save_recipe(user,recipe)
        elif numRecipe <= MAX_RECIPE_FREE:
            result,mess= save_recipe(user,recipe)
        else:
            mess="You are using a free version which limited on number of recipe storage.\n Please upgrading pro version for full option!"
        messages.info(request, mess)

    context = {
        "recipe": recipe,
    }
    return render(request, "detail.html", context)




# user page
@login_required(login_url='login')
def user_profile(request):
    user = request.user.profile
    try:
        results = DB_Recipe.objects.filter(user=user, original=False) 
        # select * from DB_Recipe where user = user and original = False
        topic = "all"
        query = request.user.username
        total = results.count()
        original_results = DB_Recipe.objects.filter(user=user, original=True)
        original_total =  original_results.count()
    except:
        results = []
        topic = "all"
        query = request.user.username
        total = results.count()
        original_results = DB_Recipe.objects.filter(user=user, original=True)
        original_total =  original_results.count()



    #paginate results
    paginator = Paginator(results, 3)
    original_paginator = Paginator(original_results, 3)
    page = request.GET.get("page", 1)
    original_page = request.GET.get("original_page", 1)
    try:
        results = paginator.page(page)
        original_results = original_paginator.page(original_page)
    except PageNotAnInteger:
        results = paginator.page(1)
        original_results = original_page.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)
        original_results = original_page.page(original_page.num_pages)

    context = {
        "topic":topic,
        "page":page,
        "total":total,
        "query":query,
        "results":results,
        "original_results" : original_results,
        "original_total" : original_total,
        "original_page" : original_page,
    }

    return render(request, "user.html",context)

def SignupPage(request):
    if request.method=='POST':
        try:
            uname=request.POST.get('username')
            email=request.POST.get('email')
            pass1=request.POST.get('password1')
            pass2=request.POST.get('password2')
            if pass1!=pass2:
                messages.error(request,"Your password and confirm password are not Same!!")
            else:
                my_user=User.objects.create_user(uname,email,pass1)
                my_user.save()

                my_profile = Profile(user=my_user, username=my_user.username, email=my_user.email )
                my_profile.save()  

                messages.success(request,"User Added!")
                return redirect('login')                            
        except:
            messages.error(request,"Missing Value!")
        

    return render(request,'signup.html')

def LoginPage(request):
    if request.method == 'GET':
        nextUrl = request.GET.get('next', None)

    if request.method=='POST':
            username=request.POST.get('username')
            pass1=request.POST.get('pass')
            user=authenticate(request,username=username,password=pass1)
            if user is not None:
                login(request,user)
                nextUrl=request.POST.get('next',None)
                if nextUrl != "":
                    return redirect(nextUrl)
                else:
                    return redirect('user')
            else:
                messages.error(request,"Username or Password is incorrect!!!")

    return render(request,'login.html')

def LogoutPage(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def user_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            emailF = form["email"].value()
            userFname = form["username"].value()            

            form.save()
            user = User.objects.get(username = request.user.username)
            if userFname != user.username:
                user.username = userFname
            if emailF != user.email:
                user.email = emailF
            
            user.save()
            
            messages.success(request, f'{request.user.username} is updated.')
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, form_validation_error(form))

    else:
        form = ProfileForm(instance=request.user.profile)
    context = {'form':form}
    return render(request, 'user-editor.html',context)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
#create recipe for user
@login_required(login_url='login')
def user_create_recipe(request):
    # if request.method == 'POST':
    #     form = RecipeForm(request.POST, request.FILES)
    #     if form.is_valid():
    #         try:
    #             DB_Recipe.objects.get(title=RecipeForm.title,user=request.user)
    #             return False,"The Recipe was saved"
    #         except:
    #             try:
    #                 logging.debug(RecipeForm.title)
    #                 DB_Recipe(title= RecipeForm.title,
    #                         # image = RecipeForm.image,
    #                         description= RecipeForm.description,
    #                         ingredients= RecipeForm.ingredients,
    #                         directions = RecipeForm.directions,
    #                         servings = RecipeForm.servings,
    #                         time = RecipeForm.time,
    #                         calories = RecipeForm.calories,
    #                         fat = RecipeForm.fat,
    #                         carbs = RecipeForm.carbs,
    #                         protein = RecipeForm.protein,
    #                         topic = RecipeForm.topic,
    #                         user = request.user).save()
    #                 return redirect(request.META.get('HTTP_REFERER'))
    #             except:
    #                 return False,"Fail to save!"
    # else:
    #     form = RecipeForm()
    # return render(request, 'user-create-recipe.html', {'form': form})
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            
            form.save()
            print("aaaaa")
            messages.success(request, f'{request.user.username} is updated.')
            return redirect(request.META.get('HTTP_REFERER'))
        else:   
            print("bbbbb")
            messages.error(request, form_validation_error(form))

    else:
        print("vvvvv")
        # form = ProfileForm(instance=request.user.profile)
        form = RecipeForm(instance=request.user)
    context = {'form':form}
    return render(request, 'user-create-recipe.html',context)
##############################

@login_required(login_url='login')
def delete_recipe(request, item_id):
    item = get_object_or_404(DB_Recipe, id=item_id)
    item.delete()

    # Add a success message
    messages.success(request, 'Item removed successfully')

    # Redirect back to the previous page
    return redirect(request.META.get('HTTP_REFERER'))


def detail(request, slug):
    recipe = get_object_or_404(DB_Recipe, slug=slug, user= request.user.profile)
    context = {
        "recipe":recipe,
    }
    return render(request, "detail.html", context)

def search_DB(request):
    recipes = DB_Recipe.objects.all()

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


def test(request):
    return render(request,"test.html")

#Paypal
def checkout(request):
    return render(request, "payment/clientside_checkout.html")

@login_required(login_url='login',redirect_field_name="next")
def process_payment(request):
    current_user = request.user.profile
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': 0.01,
        'item_name': '{}-{} Upgrade Vetula Pro'.format(current_user.username,str(current_user.id)),
        'currency_code': 'USD',
        'invoice': '{}-{}'.format(str(current_user.id),request.user.email),
        'notify_url': request.build_absolute_uri(reverse('paypal-ipn')),
        'return_url': request.build_absolute_uri(reverse('successful')),
        'cancel_return': request.build_absolute_uri(reverse('cancelled')),
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {'form': form}
    return render(request, 'payment/serverside_checkout.html',context=context)


@csrf_exempt
def payment_done(request):
    return render(request, 'payment/successful.html')


@csrf_exempt
def payment_cancelled(request):
    return render(request, 'payment/cancelled.html')
