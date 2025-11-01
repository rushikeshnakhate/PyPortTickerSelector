from enum import Enum

import pytest

pytest.importorskip("redis")

from src.cache.cache_factory import CacheFactory
from src.cache.panda_cache import PandasCache
from src.cache.redis_cache import RedisCache
from src.cache.sqlite_cache import SQLiteCache
from src.utils.constants import CacheType


class DummyRedisClient:
    def __init__(self, *args, **kwargs):
        pass

    def get(self, key):
        return None

    def setex(self, key, ttl, value):
        return True

    def exists(self, key):
        return 0


class TestCacheFactory:
    def test_returns_singleton_instances(self, monkeypatch):
        monkeypatch.setattr(CacheFactory, "_cache_instances", {})
        monkeypatch.setattr(PandasCache, "_instance", None)
        monkeypatch.setattr(SQLiteCache, "_instance", None)
        monkeypatch.setattr(RedisCache, "_instance", None)
        monkeypatch.setattr("src.cache.redis_cache.redis.Redis", DummyRedisClient)

        pandas_cache = CacheFactory.get_cache(CacheType.PANDAS)
        sqlite_cache = CacheFactory.get_cache(CacheType.SQLITE)
        redis_cache = CacheFactory.get_cache(CacheType.REDIS)

        assert isinstance(pandas_cache, PandasCache)
        assert isinstance(sqlite_cache, SQLiteCache)
        assert isinstance(redis_cache, RedisCache)

        assert CacheFactory.get_cache(CacheType.PANDAS) is pandas_cache
        assert CacheFactory.get_cache(CacheType.SQLITE) is sqlite_cache
        assert CacheFactory.get_cache(CacheType.REDIS) is redis_cache

    def test_unknown_cache_type_raises_value_error(self, monkeypatch):
        monkeypatch.setattr(CacheFactory, "_cache_instances", {})

        class UnknownCache(Enum):
            UNKNOWN = "unknown"

        with pytest.raises(ValueError):
            CacheFactory.get_cache(UnknownCache.UNKNOWN)

