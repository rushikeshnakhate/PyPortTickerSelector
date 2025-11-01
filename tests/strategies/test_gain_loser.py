import pytest
import pandas as pd

from src.strategies.top_gainers.top_gainers import TopGainersStrategy
from src.strategies.top_gainers.top_gainers_RSI_Strategy import TopGainersRSIStrategy
from src.strategies.top_gainers.top_gainers_combined_strategy import TopGainersCombinedStrategy
from src.strategies.top_loosers.top_losers import TopLosersStrategy


@pytest.fixture
def mock_stock_data():
    """Returns a mock dataframe with necessary columns for all strategies"""
    return pd.DataFrame({
        "Ticker": ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA"],
        "ExponentialMovingAverage": [150, 250, 2800, 3400, 900],
        "BollingerBands": [
            {"Upper Band": 155, "Lower Band": 145},
            {"Upper Band": 255, "Lower Band": 245},
            {"Upper Band": 2850, "Lower Band": 2750},
            {"Upper Band": 3450, "Lower Band": 3350},
            {"Upper Band": 950, "Lower Band": 850}
        ],
        "RelativeStrengthIndex": [70, 65, 60, 75, 80]
    })


def test_top_gainers_strategy(mock_stock_data):
    strat = TopGainersStrategy(df=mock_stock_data, top_n=3)
    result = strat.run()
    assert isinstance(result, list)
    assert len(result) == 3
    assert all("ticker" in r and "gain" in r for r in result)


def test_top_gainers_combined_strategy(mock_stock_data):
    strat = TopGainersCombinedStrategy(df=mock_stock_data, top_n=2)
    result = strat.run()
    assert isinstance(result, list)
    assert len(result) == 2
    assert all("ticker" in r and "combined_gain" in r for r in result)


def test_top_gainers_rsi_strategy(mock_stock_data):
    strat = TopGainersRSIStrategy(df=mock_stock_data, top_n=2)
    result = strat.run()
    assert isinstance(result, pd.DataFrame)
    assert result.shape[0] == 2
    assert all(col in result.columns for col in ["Ticker", "Gain"])


def test_top_losers_strategy(mock_stock_data):
    strat = TopLosersStrategy(df=mock_stock_data, top_n=2)
    result, = strat.run() if isinstance(strat.run(), tuple) else strat.run()
    # If run returns a list directly
    if isinstance(result, list):
        assert len(result) == 2
        assert all("ticker" in r and "loss" in r for r in result)
