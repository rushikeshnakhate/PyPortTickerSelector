import pandas as pd

from src.strategies.base_strategy import BaseStrategy
from src.strategies.top_loosers.top_losers import TopLosersStrategy


class DummyStrategy(BaseStrategy):
    def run(self):
        return [
            {"ticker": "AAA", "gain": 10},
            {"ticker": "BBB", "gain": 5},
            {"ticker": "CCC", "gain": 1},
        ]


def create_dataframe() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "Ticker": "AAA",
            "BollingerBands": {"Lower Band": 90.0},
            "ExponentialMovingAverage": 100.0,
        },
        {
            "Ticker": "BBB",
            "BollingerBands": "{'Lower Band': np.float64(110.0)}",
            "ExponentialMovingAverage": 120.0,
        },
        {
            "Ticker": "CCC",
            "BollingerBands": {},
            "ExponentialMovingAverage": 80.0,
        },
    ])


class TestBaseStrategyUtils:
    def test_get_tickers_from_dataframe(self):
        strategy = DummyStrategy(pd.DataFrame({"Ticker": ["A", "B", "C"], "gain": [3, 2, 1]}), top_n=2)
        tickers = strategy.get_tickers(strategy.df)
        assert tickers == ["A", "B"]

    def test_get_tickers_from_list(self):
        strategy = DummyStrategy(pd.DataFrame({"Ticker": []}), top_n=2)
        tickers = strategy.get_tickers(["X", "Y", "Z"])
        assert tickers == ["X", "Y"]


class TestTopLosersStrategy:
    def test_returns_sorted_losers(self):
        df = create_dataframe()
        strategy = TopLosersStrategy(df, top_n=3)
        results = strategy.run()

        assert len(results) == 3
        assert results[0]["ticker"] == "CCC"
        assert results[-1]["ticker"] == "AAA"

    def test_invalid_bollinger_data_defaults_to_zero(self):
        df = pd.DataFrame([
            {
                "Ticker": "DDD",
                "BollingerBands": "not-a-dict",
                "ExponentialMovingAverage": 50.0,
            }
        ])

        strategy = TopLosersStrategy(df, top_n=1)
        results = strategy.run()
        assert results[0]["loss"] == 0

