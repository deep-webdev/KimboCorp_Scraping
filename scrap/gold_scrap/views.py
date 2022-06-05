from django.shortcuts import render
from . import models
from gold_scrap.schedular import apmex,sdbullion,silverbullion
# Create your views here.
def index(request):
     silverbullion.update_data()
     apmex.update_data()
     sdbullion.update_data()
     return render(request, 'base.html')


def extracted(request):
     data = models.Extracted.objects.all()
     return render(request,'index.html',{'data':data})