import pandas as pd

from src.strategies.top_gainers.top_gainers import TopGainersStrategy
from src.strategies.top_gainers.top_gainers_RSI_Strategy import TopGainersRSIStrategy
from src.strategies.top_gainers.top_gainers_combined_strategy import TopGainersCombinedStrategy


def create_strategy_dataframe() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "Ticker": "AAA",
            "BollingerBands": {"Upper Band": 100.0},
            "ExponentialMovingAverage": 110.0,
            "RelativeStrengthIndex": 60.0,
        },
        {
            "Ticker": "BBB",
            "BollingerBands": "{'Upper Band': np.float64(120.0)}",
            "ExponentialMovingAverage": 108.0,
            "RelativeStrengthIndex": 55.0,
        },
        {
            "Ticker": "CCC",
            "BollingerBands": {"Upper Band": 95.0},
            "ExponentialMovingAverage": 90.0,
            "RelativeStrengthIndex": 40.0,
        },
    ])


class TestTopGainersStrategy:
    def test_returns_sorted_gainers_by_percentage(self):
        df = create_strategy_dataframe()
        result = TopGainersStrategy(df, top_n=2).run()

        assert len(result) == 2
        assert result[0]["ticker"] == "AAA"
        assert result[0]["gain"] > result[1]["gain"]


class TestTopGainersRSIStrategy:
    def test_returns_top_n_by_rsi(self):
        df = create_strategy_dataframe()
        result_df = TopGainersRSIStrategy(df.copy(), top_n=2).run()

        assert list(result_df["Ticker"]) == ["AAA", "BBB"]
        assert list(result_df["Gain"]) == [60.0, 55.0]


class TestTopGainersCombinedStrategy:
    def test_combined_strategy_sorts_by_combined_gain(self):
        df = create_strategy_dataframe()
        result = TopGainersCombinedStrategy(df, top_n=2).run()

        assert len(result) == 2
        assert result[0]["ticker"] == "AAA"
        assert result[0]["combined_gain"] >= result[1]["combined_gain"]

