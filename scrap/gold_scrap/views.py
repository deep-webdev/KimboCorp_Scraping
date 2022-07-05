from django.http import JsonResponse
from django.shortcuts import render
from . models import *
from gold_scrap.schedular import apmex,sdbullion,silverbullion
from django.db.models import Min
from django.apps import apps
from pycoingecko import CoinGeckoAPI
import pandas as pd 
from itertools import chain

# Create your views here.
def index(request):
     return render(request, 'base.html')


def extracted(request):
     data = Extracted.objects.all()
     return render(request,'index.html',{'data':data})


def get_suplier_data(name):
     data = name.objects.all()
     cg = CoinGeckoAPI()
     crypto_price = cg.get_price(ids='bitcoin,tether,ethereum', vs_currencies='usd')
     df_final = pd.DataFrame(list(data.values()))
     df_final['Fees'] = 0.8
     df_final['Commissions'] = 0.5
     df_final['price_usd'] = df_final['price_usd'].astype(float)
     df_final['Final_Price'] = df_final['price_usd'] + df_final['price_usd'] * (df_final['Fees']/100) + df_final['price_usd'] * (df_final['Commissions']/100)
     df_final['Bitcoin_Price'] = round(df_final['Final_Price'] / crypto_price['bitcoin']['usd'], 4)
     df_final['Ethereum_Price'] = round(df_final['Final_Price'] / crypto_price['ethereum']['usd'], 4)
     df_final['Tether_Price'] = round(df_final['Final_Price'] / crypto_price['tether']['usd'], 4)
     return df_final.to_dict('records')

def all_products(request):
     suplier_name = Extracted.objects.filter().values_list('supplier_name').annotate(Min('price_usd')).order_by('price_usd')[0]
     model_details ={
          'Silver Bullion':'SilverBullion',
          'APMEX': 'Apmex',
          'Bullion Star':'BullionStar',
          'Indigo precious metals':'IndigoPrecious',
          'SDbullion':'SDBullion',
          'Gold Silver Central':'GoldCentral',
          'Kitco':'Kitco'
     }
     Model = apps.get_model('gold_scrap', model_details[suplier_name[0]])
     data = get_suplier_data(Model)
     price_table = get_price_table()
     return render(request,'product.html',{'data':data, 'price_table':price_table,'name': model_details[suplier_name[0]]})


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
     silverbul = SilverBullion.objects.all()
     indigorecious = IndigoPrecious.objects.all()
     apmex = Apmex.objects.all()
     bullion = BullionStar.objects.all()
     sdbul = SDBullion.objects.all()
     goldcentral = GoldCentral.objects.all()
     kitco = Kitco.objects.all()
     result_list = list(chain(silverbul,indigorecious, apmex, bullion, sdbul, goldcentral, kitco))
     price_table = get_price_table()
     for i in result_list:
          if 'oz' in i.weight:
               print(i)
               i.weight = str(price_table['spot'] * convert_to_float(i.weight.split(" ")[0])) + ' g'
     return render(request, 'allProducts.html', {'data': result_list, 'price_table':price_table})