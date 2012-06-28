from django.utils import simplejson
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from dolphin import flipper, settings, utils
from dolphin.models import FeatureFlag

def json(request, direct=False):
    active_flags = flipper.active_flags(request=request)
    j = simplejson.dumps({'active_flags': [f.name for f in active_flags]})
    if direct:
        return j
    return HttpResponse(j, content_type='application/json')

def js(request):
    active_flags = json(request, direct=True)
    resp = render_to_response('dolphin/dolphin_js.js',
                              {'active_flags':active_flags})

    resp['Content-Type'] = 'application/javascript'
    return resp

@flipper.switch_is_active(settings.DOLPHIN_TEST_FLAG)
def dolphin_test(request):
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

    return render_to_response('dolphin/dolphin_test.html', context_instance=context)
