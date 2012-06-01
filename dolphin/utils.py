from math import sin, cos, degrees, acos, radians

from django.conf import settings

def calc_dist(lat_A, long_A, lat_B, long_B):
    """Taken from the zip code database project"""
    distance = (sin(radians(lat_A)) *
                sin(radians(lat_B)) +
                cos(radians(lat_A)) *
                cos(radians(lat_B)) *
                cos(radians(long_A - long_B)))

    distance = (degrees(acos(distance))) * 69.09

    return distance

def get_ip(request):
    """
    Returns the REMOTE_ADDR of the request.
    Assumes it's set correctly by middleware.
    """
    #use hasattr to avoid fake requests in tests
    if hasattr(request, 'META'):
        return request.META.get('REMOTE_ADDR', "0.0.0.0")
    return '0.0.0.0'

def get_geoip_coords(ip):
    """
    Returns (lat, lon) for the ip if it's valid or None
    """
    if getattr(settings, 'DOLPHIN_USE_GIS', True) != True:
        return None

    #assume that GIS is set up properly with a setting for the path
    #if not, it'll raise an exception
    from django.contrib.gis.geoip import GeoIP
    gip = GeoIP()
    return gip.lat_lon(ip)
