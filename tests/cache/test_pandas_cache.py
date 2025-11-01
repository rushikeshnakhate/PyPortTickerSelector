import pickle
from datetime import datetime, timedelta

from src.cache.panda_cache import PandasCache


class TestPandasCache:
    def test_set_get_and_exists(self, tmp_path, monkeypatch):
        monkeypatch.setattr(PandasCache, "_instance", None)

        cache = PandasCache(base_path=str(tmp_path))
        key = "sample_key"
        value = {"foo": "bar"}

        cache.set(key, value, ttl=120)

        assert cache.exists(key) is True
        assert cache.get(key) == value

    def test_expired_entries_are_removed(self, tmp_path, monkeypatch):
        monkeypatch.setattr(PandasCache, "_instance", None)

        cache = PandasCache(base_path=str(tmp_path))
        key = "expiring_key"
        value = {"data": 123}

        cache.set(key, value, ttl=60)

        cache_path = tmp_path / f"{key}.pkl"
        with cache_path.open("rb") as handle:
            payload = pickle.load(handle)

        payload["expires_at"] = datetime.utcnow() - timedelta(seconds=5)

        with cache_path.open("wb") as handle:
            pickle.dump(payload, handle)

        assert cache.get(key) is None
        assert cache.exists(key) is False

