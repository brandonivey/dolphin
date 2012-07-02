from dolphin import settings
from .middleware import RequestStoreMiddlewareTest

if settings.DOLPHIN_USE_REDIS:
    from .redis import (RedisActiveTest, RedisUserFlagsTest, RedisGeoIPTest,
                        RedisABTest, RedisCustomFlagTest, RedisActiveTagTest, RedisFlagListTest)
else:
    from .flipper import ActiveTest, UserFlagsTest, GeoIPTest, ABTest, CustomFlagTest
    from .templatetags import ActiveTagTest, FlagListTest
    from .testutils import SetActiveTest
