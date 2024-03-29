from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('',views.extracted,name='home'),
    path('product/',views.all_products,name='products'),
    path('crypt_price/',views.get_crypto_price,name="crypto_price"),
    path('all_products/', views.all_supp_products, name='all_prod'),
    path('update_extracted',views.update_extracted,name='update_extracted')
]