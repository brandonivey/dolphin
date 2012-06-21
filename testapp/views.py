from dolphin import flipper
from dolphin.models import FeatureFlag
from django.http import HttpResponse
from django.shortcuts import render_to_response

def home(request):
    return render_to_response('home.html', {'object_list':FeatureFlag.objects.all(), 'request':request})

def is_active(request, slug):
    return HttpResponse(str(flipper.is_active(slug)))
