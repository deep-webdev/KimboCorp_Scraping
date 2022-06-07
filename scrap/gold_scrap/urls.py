from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('',views.extracted,name='home'),
    path('product/',views.all_products,name='products'),
    path('crypt_price/',views.get_crypto_price,name="crypto_price")
]