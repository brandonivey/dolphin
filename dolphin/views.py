from django.utils import simplejson
from django.http import HttpResponse
from django.shortcuts import render_to_response

from dolphin import flipper

def json(request, direct=False):
    active_flags = flipper.active_flags(request=request)
    j = simplejson.dumps({'active_flags': [f.name for f in active_flags]})
    if direct:
        return j
    return HttpResponse(j, content_type='application/json')

def js(request):
    active_flags = json(request, direct=True)
    resp = render_to_response('dolphin_js.js',
                              {'active_flags':active_flags})

    resp['Content-Type'] = 'application/javascript'
    return resp
