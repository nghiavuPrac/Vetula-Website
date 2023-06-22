from django.urls import path, include
from .views import *



urlpatterns = [
    path("", home, name="home"),
    path("user", user_profile, name="user"),
    path("user/edit/", user_edit, name="user-edit"),    
    path("user/remove-item/<int:item_id>/", delete_recipe, name ="remove_item"),
    
    path("signup/", SignupPage, name="signup"),
    path("login/", LoginPage, name="login"),
    path("logout/", LogoutPage, name="logout" ),

    path("search/", search_API, name="search"),
    #path("search", search_DB, name="search"),
    path("detail/<str:index>", recipe_detail, name ="recipe_detail"),

    path("<slug>", detail, name="detail"),

    path('user/checkout/', checkout, name= "checkout"),

    path('user/process-payment/', process_payment, name='process_payment'),
    path('user/process-payment/successful', payment_done, name="successful" ),
    path('user/process-payment/cancelled', payment_cancelled, name="cancelled" ),
    
  ]