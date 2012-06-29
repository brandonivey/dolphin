from dolphin import settings
from .testutils import SetActiveTest
from .flipper import (ActiveTest, UserFlagsTest, GeoIPTest, ABTest, CustomFlagTest,
                      SessionTest)
from .templatetags import ActiveTagTest, FlagListTest
from .middleware import RequestStoreMiddlewareTest
if settings.DOLPHIN_USE_REDIS:
    from .redis import (RedisActiveTest, RedisUserFlagsTest, RedisGeoIPTest,
                        RedisABTest, RedisCustomFlagTest, RedisActiveTagTest, RedisFlagListTest)
