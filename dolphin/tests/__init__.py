from dolphin import settings, flipper
from dolphin.backends.djbackend import DjangoBackend
from .middleware import RequestStoreMiddlewareTest

if isinstance(flipper.backend, DjangoBackend):
    from .admin import AdminTest
    from .flipper import ActiveTest, UserFlagsTest, GeoIPTest, ABTest, CustomFlagTest, RollOutTest, CookiesTest
    from .templatetags import ActiveTagTest, FlagListTest
    from .testutils import SetActiveTest

else:
    from .redis import (RedisActiveTest, RedisUserFlagsTest, RedisGeoIPTest,
                        RedisABTest, RedisCustomFlagTest, RedisActiveTagTest, RedisFlagListTest)
