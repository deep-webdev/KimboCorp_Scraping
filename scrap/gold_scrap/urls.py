from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('',views.extracted),
    path('product/',views.all_products)
]