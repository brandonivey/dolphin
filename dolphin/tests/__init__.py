from .testutils import SetActiveTest
from .flipper import ActiveTest, UserFlagsTest, GeoIPTest, ABTest, CustomFlagTest
from .templatetags import ActiveTagTest, FlagListTest
from .middleware import RequestStoreMiddlewareTest
from .redis import (RedisActiveTest, RedisUserFlagsTest, RedisGeoIPTest,
                    RedisABTest, RedisCustomFlagTest)
