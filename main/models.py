from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

from autoslug import AutoSlugField
from django.shortcuts import reverse, redirect
import datetime

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete= models.CASCADE)

    username = models.CharField(max_length=200, null=True, blank= True)

    firstname = models.CharField(max_length=100, null=True, blank= True)

    lastname = models.CharField(max_length=100, null=True, blank= True)

    occupation = models.CharField(max_length=200, null=True, blank= True)

    location = models.CharField(max_length=200, null=True, blank= True)

    phone = models.CharField(max_length=20, blank=True, null=True)

    birthday = models.DateField(default=now, blank=True, null =True)

    about = models.TextField(default="I love cooking")

    avatar_pic =  models.ImageField(default = 'image/user_default.png', upload_to = 'user-avatar', null = True, blank = True)

    purchase = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s profile"

class API_Recipe():
    def __init__(self,data, index):
        self.index = index
        self.title = data["label"]
        self.image = data["image"]
        self.description = self.list_to_string(" * ",data["healthLabels"])
        self.ingredients = self.list_to_string("\n",["- "+item for item in data["ingredientLines"]])
        self.servings = data["yield"]
        self.directions = data["url"]
        self.time = data["totalTime"]
        self.calories = round(data["calories"],2)
        self.fat = round(data["totalNutrients"]["FAT"]['quantity'],2)
        self.protein = round(data["totalNutrients"]['PROCNT']['quantity'],2)
        self.carbs = round(data["totalNutrients"]['CHOCDF']['quantity'],2)
        self.topic = data["cuisineType"]

    def __str__(self):
        self.title

    def save(self):
        return reverse("recipe_detail",kwargs={"index":self.index})

    def list_to_string(self,separator,itemList):
        return separator.join(itemList)
    
    
    def get_url(self):
        return reverse("recipe_detail",kwargs={"index":self.index})

class Topic(models.Model):
    title = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from="title")

    def __str__(self):
        return self.title

class DB_Recipe(models.Model):
    title = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from="title")
    image = models.CharField(max_length=400)
    description = models.TextField()
    ingredients = models.TextField()
    directions = models.CharField(max_length=100)
    servings = models.CharField(max_length=5)
    time = models.CharField(max_length=5)
    calories = models.CharField(max_length=5)
    fat = models.CharField(max_length=5)
    carbs = models.CharField(max_length=5)
    protein = models.CharField(max_length=5)
    topic = models.CharField(max_length=50)

    user = models.ForeignKey(Profile, on_delete=models.CASCADE)

    original = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title

    def get_url(self):
        return reverse("detail", kwargs={
            "slug":self.slug,
        })
