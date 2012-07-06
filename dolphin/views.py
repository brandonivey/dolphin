from django.utils import simplejson
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from dolphin import flipper, settings, utils
from dolphin.models import FeatureFlag

def _active_flags(request):
    """Returns the active flags for the request."""
    active_flags = flipper.active_flags(request=request)
    return simplejson.dumps({'active_flags': [f.name for f in active_flags]})

def json(request, direct=False):
    """Returns the active flags in a json response."""
    return HttpResponse(_active_flags(request), content_type='application/json')

def js(request):
    """Returns the active flags in as a javascript file with a flipper object"""
    active_flags = _active_flags(request)
    resp = render_to_response('dolphin_js.js',
                              {'active_flags':active_flags})

    resp['Content-Type'] = 'application/javascript'
    return resp

@flipper.switch_is_active(settings.DOLPHIN_TEST_FLAG)
def dolphin_test(request):
    """A test page to verify the flags dolphin considers active"""
    user_info = {'Authenticated':request.user.is_authenticated(),
                 'Is Staff':request.user.is_staff,
                 'Username':request.user.username}
    if settings.DOLPHIN_USE_GIS:
        user_info['Geolocation'] = utils.get_geoip_coords(utils.get_ip(request))

    context = RequestContext(request,
                             {
                                 'user_info':user_info,
                                 'flags':flipper.all_flags(request=request),
                                 'flipper':flipper
                             })

    return render_to_response('dolphin_test.html', context_instance=context)
