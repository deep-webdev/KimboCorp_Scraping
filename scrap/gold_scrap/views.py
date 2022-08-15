from distutils.sysconfig import customize_compiler
from django.http import JsonResponse
from django.shortcuts import render
from . models import *
from gold_scrap.schedular import apmex,sdbullion,silverbullion
from django.db.models import Min
from django.apps import apps
from pycoingecko import CoinGeckoAPI
import pandas as pd 
from itertools import chain
import mysql.connector

# Create your views here.
def index(request):
     return render(request, 'base.html')


def extracted(request):
     connection = mysql.connector.connect(user='gold_scrap', database='gold_scrap', host='localhost', password="Gold_scrap@123", port='3306', auth_plugin='mysql_native_password')
     if connection.is_connected():
          cursor = connection.cursor()
          my_query = """SELECT * FROM extracted;""";
          data = cursor.execute(my_query)
          result = cursor.fetchall()
          cursor.close()
          connection.close()
     return render(request,'index.html',{'data':result})


def update_extracted(request):
     connection = mysql.connector.connect(user='gold_scrap', database='gold_scrap', host='localhost', password="Gold_scrap@123", port='3306', auth_plugin='mysql_native_password')
     if connection.is_connected():
          cursor = connection.cursor()
          my_query = """SELECT * FROM extracted;""";
          data = cursor.execute(my_query)
          result = cursor.fetchall()
          cursor.close()
          connection.close()
     return JsonResponse({'data':result})


def all_products(request):
     
     connection = mysql.connector.connect(user='gold_scrap', database='gold_scrap', host='localhost', password="Gold_scrap@123", port='3306', auth_plugin='mysql_native_password')
     if connection.is_connected():
          cursor = connection.cursor()
          my_query = """SELECT Supplier_name FROM extracted WHERE Price =  ( SELECT MIN(Price) FROM extracted where Price != 0 ) """;
          cursor.execute(my_query)
          result = cursor.fetchone()
          my_query = """SELECT * FROM gold_data WHERE Supplier_name=%s;""";
          cursor.execute(my_query, [result[0]])
          data = cursor.fetchall()
     price_table = get_price_table()
     return render(request,'product.html',{'data':data, 'price_table':price_table})


def get_spot():
     data = apmex.scraping('https://www.monex.com/gold-prices/')
     dfs = data[0]
     soup = data[1]
     spot = float(dfs[0]['Today'][0].replace('$','').replace(',',''))
     return spot


def get_price_table():
     cg = CoinGeckoAPI()
     crypto_price = cg.get_price(ids='bitcoin,tether,ethereum', vs_currencies='usd')
     crypto_price['spot'] = get_spot()
     return crypto_price


def get_crypto_price(request):
     crypto_price = get_price_table()
     return JsonResponse(crypto_price)


def convert_to_float(frac_str):
     try:
          return float(frac_str)
     except ValueError:
          num, denom = frac_str.split('/')
          try:
               leading, num = num.split(' ')
               whole = float(leading)
          except ValueError:
               whole = 0
          frac = float(num) / float(denom)
          return whole - frac if whole < 0 else whole + frac


def all_supp_products(request):
     connection = mysql.connector.connect(user='gold_scrap', database='gold_scrap', host='localhost', password="Gold_scrap@123", port='3306', auth_plugin='mysql_native_password')
     if connection.is_connected():
          cursor = connection.cursor()
          my_query = """SELECT * FROM gold_data;""";
          cursor.execute(my_query)
          result = cursor.fetchall()
          cursor.close()
     price_table = get_price_table()
     return render(request, 'allProducts.html', {'data': result, 'price_table':price_table})