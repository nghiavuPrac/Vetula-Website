from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages



from .forms import  ProfileForm,form_validation_error
from paypalrestsdk import Payment
from .models import DB_Recipe, API_Recipe, Profile
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from . import api_config
# from py_edamam import Edamam

#import food_extraction
import subprocess as sp
import json
import os
import requests


# ed_handler = Edamam(recipes_appid=api_config.recipes_appid,
#                  recipes_appkey=api_config.recipes_appkey)    
app_id = api_config.recipes_appid
app_key = api_config.recipes_appkey

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
        elif numRecipe <= 10:
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
        results = DB_Recipe.objects.filter(user=user)
        topic = "all"
        query = request.user.username
        total = results.count()
    except:
        results = []
        topic = "all"
        query = request.user.username
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

    return render(request, "user.html",context)

def SignupPage(request):
    if request.method=='POST':
        try:
            uname=request.POST.get('username')
            email=request.POST.get('email')
            pass1=request.POST.get('password1')
            pass2=request.POST.get('password2')
            if pass1!=pass2:
                messages.error(request,"Your password and confrom password are not Same!!")
            else:
                my_user=User.objects.create_user(uname,email,pass1)
                my_user.save()

                my_profile = Profile(user=my_user, username=my_user.username)
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
            form.save()
            username = request.user.username
            messages.success(request, f'{username}, Your profile is updated.')
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, form_validation_error(form))

    else:
        form = ProfileForm(instance=request.user.profile)
    context = {'form':form}
    return render(request, 'user-editor.html',context)



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
def create_payment(request):
    # Generate ID
    payment_id = str(uuid.uuid4())  
    payer_id = str(uuid.uuid4())  
    
    # Set up the payment object
    #tui không rõ cái domain mình là gì , phiền sửa lại cái redirect_urls giúp tui nhé. Máy khs debug không dc
    
    payment = Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": f"http://yourdomain.com/payment/execute?paymentId={payment_id}&PayerID={payer_id}",
            "cancel_url": "http://yourdomain.com/payment/cancel"
        },
        "transactions": [{
            "amount": {
                "total": "50.000",
                "currency": "VND"
            },
            "description": "Payment for recipe ."
        }]
    })

    # Create the payment
    if payment.create():
        # Payment created successfully, redirect user to PayPal approval URL
        for link in payment.links:
            if link.method == "REDIRECT":
                redirect_url = link.href
                return redirect(redirect_url)
    else:
        # Failed to create payment, handle the error
        return render(request, 'payment_error.html', {'error': payment.error})
    
def execute_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    if not payment_id or not payer_id:
        return render(request, 'payment_error.html', {'error': 'Payment information missing.'})

    payment = Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        # Payment executed successfully, handle the success scenario
        return render(request, 'payment_success.html')
    else:
        # Failed to execute payment, handle the error
        return render(request, 'payment_error.html', {'error': payment.error})
