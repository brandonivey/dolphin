import re
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

import datetime
from geoposition import Geoposition

def cache_key(name):
    m = md5()
    m.update(name)
    return 'dolphin_' + str(m.hexdigest())

class Schema(object):

    @staticmethod
    def _bool(x):
        return True if x == 'True' else False

    bool_fields = set(('registered_only', 'enabled', 'staff_only', 'random',
                   'limit_to_users', 'enable_geo'))

    unicode_fields = set(('name',))
    datetime_fields = set(('b_test_start', 'b_test_end'))
    int_fields = set(('current_b_tests', 'maximum_b_tests'))
    float_fields = set(('radius',))
    none_fields = unicode_fields.union(datetime_fields).union(int_fields).union(float_fields)

    def parse(self, d):
        number_re = re.compile(r'(-?\d+(?:\.\d+)?)')
        for key in d.keys():
            if key in self.none_fields and (d[key] == 'None' or d[key] is None):
                d[key] = None
                continue
            if key in self.bool_fields:
                d[key] = True if d[key] == 'True' else False
            elif key in self.unicode_fields:
                d[key] = unicode(d[key])
            elif key in self.datetime_fields:
                if not isinstance(d[key], datetime.datetime):
                    d[key] = datetime.datetime.fromtimestamp(float(d[key]))
            elif key in self.int_fields:
                d[key] = int(d[key])
            elif key in self.float_fields:
                if not isinstance(key, float):
                    d[key] = float(number_re.findall(d[key])[0])
            elif key == 'center':
                if not isinstance(d[key], Geoposition):
                    l = number_re.findall(d[key])
                    #using a DefaultDict since the GeoPosition key is an object
                    d[key] = Geoposition(float(l[0]), float(l[1]))
            elif key == 'users':
                d[key] = [int(i) for i in number_re.findall(d[key])]
            else:
                del d[key]
        return d

    def serialize(self, d):
        for field in self.datetime_fields:
           if field in d and d[field] is not None:
               d[field] = d[field].strftime('%s')
        return d

