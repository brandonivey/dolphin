from dolphin import flipper
from django.http import HttpResponse

def is_active(request, slug):
    return HttpResponse(str(flipper.is_active(slug)))
