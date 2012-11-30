import re
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

import datetime
import dateutil.parser
from geoposition import Geoposition
from django.contrib.auth.models import Group
from django.utils.importlib import import_module

def cache_key(name):
    m = md5()
    m.update(name)
    return 'dolphin_' + str(m.hexdigest())

class Schema(object):

    @staticmethod
    def _bool(x):
        return True if x == 'True' else False

    bool_fields = set(('registered_only', 'enabled', 'staff_only', 'random',
                   'limit_to_group', 'enable_geo', 'enable_for_sites', 'disable_for_sites'))

    unicode_fields = set(('name', 'description'))
    datetime_fields = set(('b_test_start', 'b_test_end'))
    int_fields = set(('current_b_tests', 'maximum_b_tests', 'id', 'percent', 'cookie_max_age'))
    float_fields = set(('radius',))
    none_fields = unicode_fields.union(datetime_fields).union(int_fields).union(float_fields).union(set(['group']))

    def parse(self, d):
        number_re = re.compile(r'(-?\d+(?:\.\d+)?)')
        for key in d.keys():
            if key in self.none_fields and (d[key] == 'None' or d[key] is None):
                d[key] = None
                continue
            if key in self.bool_fields:
                if not isinstance(d[key], bool):
                    d[key] = True if d[key] == 'True' else False
            elif key in self.unicode_fields:
                d[key] = unicode(d[key])
            elif key in self.datetime_fields:
                if not isinstance(d[key], datetime.datetime):
                    d[key] = dateutil.parser.parse(d[key])
            elif key in self.int_fields:
                d[key] = int(d[key])
            elif key in self.float_fields:
                if not isinstance(d[key], float):
                    d[key] = float(number_re.findall(d[key])[0])
            elif key == 'center':
                if not isinstance(d[key], Geoposition):
                    l = number_re.findall(d[key])
                    #using a DefaultDict since the GeoPosition key is an object
                    d[key] = Geoposition(float(l[0]), float(l[1]))
            elif key == 'group':
                if not isinstance(d[key], int):
                    d[key] = int(number_re.findall(d[key])[0])
            else:
                del d[key]
        return d

    def serialize(self, d):
        for field in self.datetime_fields:
           if d.get(field, None) is not None:
               d[field] = d[field].isoformat()

        if d.get('group_id', None) is not None:
            d['group'] = d['group_id']
        elif d.get('group', None) is not None and isinstance(d['group'], int):
            d['group'] = d['group']
        else:
            d['group'] = None

        return d
