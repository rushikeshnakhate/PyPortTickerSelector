import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from src.performance_matrix.main import (
    PerformanceMatrixFactory,
    get_performance_metrics,
    get_performance_metrics_bulk,
)


@pytest.fixture
def mock_ticker_data():
    """Mock stock data"""
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
def mock_market_data():
    """Mock market data"""
    return pd.DataFrame({
        "Date": pd.date_range("2024-01-01", periods=5),
        "Close": [1000, 1010, 1020, 1030, 1040]
    })


@pytest.fixture
def mock_cache():
    mock_cache = MagicMock()
    mock_cache.get.return_value = None
    mock_cache.set = MagicMock()
    return mock_cache


@patch("src.performance_matrix.main.CacheFactory.get_cache")
@patch("src.performance_matrix.main.BenchmarkRelativeMetricsGroup.calculate")
@patch("src.performance_matrix.main.to_dataframe")
def test_get_performance_metrics(mock_to_df, mock_group_calc, mock_get_cache, mock_ticker_data, mock_market_data,
                                 mock_cache):
    """Test single ticker performance metrics calculation"""
    mock_get_cache.return_value = mock_cache
    mock_group_calc.return_value = {"metric1": 0.1, "metric2": 0.2}
    mock_to_df.return_value = pd.DataFrame({"dummy": [1]})

    df = get_performance_metrics(
        ticker="AAPL",
        ticker_data=mock_ticker_data,
        market_data=mock_market_data,
        start_date="2024-01-01",
        end_date="2024-01-05"
    )

    assert isinstance(df, pd.DataFrame)
    mock_group_calc.assert_called_once()
    mock_to_df.assert_called_once()


@patch("src.performance_matrix.main.get_performance_metrics")
@patch("src.performance_matrix.main.CacheFactory.get_cache")
def test_get_performance_metrics_bulk(mock_get_cache, mock_get_metrics, mock_ticker_data, mock_market_data, mock_cache):
    """Test bulk calculation for multiple tickers"""
    mock_get_cache.return_value = mock_cache
    mock_cache.get.return_value = None
    mock_get_metrics.return_value = pd.DataFrame({"metric1": [0.1], "metric2": [0.2], "Ticker": ["AAPL"]})

    tickers = ["AAPL", "MSFT"]
    result_df = get_performance_metrics_bulk(
        ticker_list=tickers,
        ticker_data_df=mock_ticker_data,
        market_data=mock_market_data,
        start_date="2024-01-01",
        end_date="2024-01-05"
    )

    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty
    mock_cache.set.assert_called_once()
    mock_get_metrics.assert_called()
