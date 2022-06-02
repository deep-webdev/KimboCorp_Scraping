from django.shortcuts import render
from . import models
# Create your views here.
def index(request):
     return render(request, 'base.html')


def extracted(request):
     data = models.Extracted.objects.all()
     print(data)
     return render(request,'extracted.html',{'data':data})