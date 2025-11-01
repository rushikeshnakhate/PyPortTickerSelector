from datetime import datetime, timedelta

from src.cache.sqlite_cache import SQLiteCache
from src.database.models.cache_models import Cache


class TestSQLiteCache:
    def test_set_get_and_exists(self, tmp_path, monkeypatch):
        monkeypatch.setattr(SQLiteCache, "_instance", None)

        db_url = f"sqlite:///{tmp_path / 'cache.db'}"
        cache = SQLiteCache(db_url=db_url)

        key = "sqlite_key"
        value = [1, 2, 3]

        cache.set(key, value, ttl=300)

        assert cache.exists(key) is True
        assert cache.get(key) == value

        cache.db_session.close()
        cache.engine.dispose()

    def test_expired_entry_is_ignored(self, tmp_path, monkeypatch):
        monkeypatch.setattr(SQLiteCache, "_instance", None)

        db_url = f"sqlite:///{tmp_path / 'cache_expire.db'}"
        cache = SQLiteCache(db_url=db_url)

        key = "expire_key"
        value = {"value": 5}

        cache.set(key, value, ttl=60)

        entry = cache.db_session.query(Cache).filter(Cache.key == key).first()
        entry.expires_at = datetime.utcnow() - timedelta(seconds=10)
        cache.db_session.commit()

        assert cache.get(key) is None
        assert cache.exists(key) is False

        cache.db_session.close()
        cache.engine.dispose()

