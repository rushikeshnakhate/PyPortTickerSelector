import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from src.indicators.main import IndicatorFactory, get_indicator, get_indicator_bulk


@pytest.fixture
def mock_ticker_data():
    """Simple mock dataframe with OHLCV columns"""
    return pd.DataFrame({
        "Date": pd.date_range("2024-01-01", periods=5),
        "Open": [100, 102, 104, 103, 105],
        "High": [101, 103, 105, 104, 106],
        "Low": [99, 101, 103, 102, 104],
        "Close": [100, 102, 104, 103, 105],
        "Volume": [1000, 1200, 1100, 1500, 1300],
        "Ticker": ["AAPL"] * 5
    })


@pytest.fixture
def mock_cache():
    """Mocked cache with get/set methods"""
    mock_cache = MagicMock()
    mock_cache.get.return_value = None  # default no cached data
    mock_cache.set = MagicMock()
    return mock_cache


@patch("src.indicators.main.CacheFactory.get_cache")
@patch("src.indicators.main.to_dataframe")
def test_calculate_all_indicators(mock_to_df, mock_get_cache, mock_ticker_data, mock_cache):
    """Test the calculation flow of all indicators"""
    mock_get_cache.return_value = mock_cache
    mock_to_df.return_value = pd.DataFrame({"dummy": [1]})

    factory = IndicatorFactory(period=14)

    # Patch indicator classes to avoid real computation
    with patch.object(factory, "_calculate_close_price_indicators", return_value={"MockClose": [1, 2, 3]}), \
            patch.object(factory, "_calculate_historical_price_indicators", return_value={"MockHist": [4, 5, 6]}):
        result = factory.calculate_all_indicators(
            ticker_data_df=mock_ticker_data,
            ticker="AAPL",
            start_date="2024-01-01",
            end_date="2024-01-05"
        )

    mock_to_df.assert_called_once()
    mock_get_cache.assert_called_once()
    assert isinstance(result, pd.DataFrame)


@patch("src.indicators.main.IndicatorFactory.calculate_all_indicators")
def test_get_indicator(mock_calc, mock_ticker_data):
    """Test that get_indicator delegates to IndicatorFactory"""
    mock_calc.return_value = pd.DataFrame({"test": [1]})

    df = get_indicator(
        ticker_data_df=mock_ticker_data,
        ticker="AAPL",
        start_date="2024-01-01",
        end_date="2024-01-05"
    )
    assert isinstance(df, pd.DataFrame)
    mock_calc.assert_called_once()


@patch("src.indicators.main.CacheFactory.get_cache")
@patch("src.indicators.main.get_indicator")
def test_get_indicator_bulk(mock_get_indicator, mock_get_cache, mock_ticker_data, mock_cache):
    """Test bulk indicator aggregation"""
    mock_get_cache.return_value = mock_cache
    mock_get_indicator.return_value = pd.DataFrame({"Indicator": [1, 2, 3]})
    mock_cache.get.return_value = None

    tickers = ["AAPL", "MSFT"]
    result_df = get_indicator_bulk(
        ticker_data_df=mock_ticker_data,
        ticker_list=tickers,
        start_date="2024-01-01",
        end_date="2024-01-05"
    )

    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty
    mock_cache.set.assert_called_once()
