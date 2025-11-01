import pandas as pd
import pytest

from src.indicators.main import IndicatorFactory, get_indicator, get_indicator_bulk
from src.utils.constants import CacheType, GLobalColumnName


class InMemoryCache:
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value, ttl=None):
        self.store[key] = value

    def exists(self, key):
        return key in self.store


@pytest.fixture
def monkeypatched_cache(monkeypatch):
    cache = InMemoryCache()

    def _get_cache(_cache_type):
        assert _cache_type == CacheType.PANDAS
        return cache

    monkeypatch.setattr("src.indicators.main.CacheFactory.get_cache", _get_cache)
    return cache


@pytest.fixture
def indicator_dataframe() -> pd.DataFrame:
    rows = 30
    data = {
        GLobalColumnName.TICKER: ["AAA"] * rows,
        "Close": [100 + i for i in range(rows)],
        "High": [101 + i for i in range(rows)],
        "Low": [99 + i for i in range(rows)],
        "Open": [100 + i for i in range(rows)],
        "Volume": [1_000_000 + i * 10_000 for i in range(rows)],
    }
    return pd.DataFrame(data)


class TestIndicatorFactoryCalculation:
    def test_calculate_selected_indicators(self, monkeypatched_cache, indicator_dataframe: pd.DataFrame):
        factory = IndicatorFactory(period=3)
        result = factory.calculate_all_indicators(
            ticker_data_df=indicator_dataframe,
            ticker="AAA",
            start_date="2024-01-01",
            end_date="2024-01-10",
            selected_indicators=["BollingerBands", "AccumulationDistributionLine"],
        )

        assert set(result.columns) >= {GLobalColumnName.TICKER, "BollingerBands", "AccumulationDistributionLine"}
        assert result.iloc[0][GLobalColumnName.TICKER] == "AAA"
        assert isinstance(result.iloc[0]["BollingerBands"], dict)
        assert result.iloc[0]["AccumulationDistributionLine"] is not None

    def test_results_are_cached(self, monkeypatched_cache, indicator_dataframe: pd.DataFrame):
        cache_key = "indicator_AAA_2024-01-01_2024-01-10"
        cached_df = pd.DataFrame({GLobalColumnName.TICKER: ["AAA"], "BollingerBands": ["cached"]})
        monkeypatched_cache.set(cache_key, cached_df)

        factory = IndicatorFactory(period=3)
        result = factory.calculate_all_indicators(
            ticker_data_df=indicator_dataframe,
            ticker="AAA",
            start_date="2024-01-01",
            end_date="2024-01-10",
            selected_indicators=["BollingerBands"],
        )

        assert result.equals(cached_df)


class TestIndicatorHelpers:
    def test_get_indicator_delegates_to_factory(self, monkeypatched_cache, indicator_dataframe: pd.DataFrame):
        df = get_indicator(
            ticker_data_df=indicator_dataframe,
            ticker="AAA",
            start_date="2024-01-01",
            end_date="2024-01-10",
            selected_indicators=["BollingerBands"],
        )
        assert GLobalColumnName.TICKER in df.columns
        assert df.iloc[0][GLobalColumnName.TICKER] == "AAA"

    def test_get_indicator_bulk_skips_missing_tickers(self, monkeypatched_cache):
        rows = 20
        df = pd.DataFrame({
            GLobalColumnName.TICKER: ["AAA"] * rows + ["BBB"] * rows,
            "Close": list(range(100, 100 + rows)) + list(range(200, 200 + rows)),
            "High": list(range(101, 101 + rows)) + list(range(201, 201 + rows)),
            "Low": list(range(99, 99 + rows)) + list(range(199, 199 + rows)),
            "Open": list(range(100, 100 + rows)) + list(range(200, 200 + rows)),
            "Volume": [1_000_000 + i * 5000 for i in range(rows)] * 2,
        })

        results = get_indicator_bulk(
            ticker_data_df=df,
            ticker_list=["AAA", "ZZZ"],
            start_date="2024-01-01",
            end_date="2024-01-02",
            selected_indicators=["BollingerBands"],
        )

        assert not results.empty
        assert set(results[GLobalColumnName.TICKER]) == {"AAA"}

