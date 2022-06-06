from django.shortcuts import render
from . models import *
from gold_scrap.schedular import apmex,sdbullion,silverbullion
from django.db.models import Min
from django.apps import apps

# Create your views here.
def index(request):
     silverbullion.update_data()
     sdbullion.update_data()
     return render(request, 'base.html')


def extracted(request):
     data = Extracted.objects.all()
     return render(request,'index.html',{'data':data})


def get_suplier_data(name):
     data = name.objects.all()
     return data

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
     return render(request,'product.html',{'data':data, 'name': model_details[suplier_name[0]]})
     
     