import numpy as np
import pandas as pd
import pytest

from src.performance_matrix.benchmark_relative_metrics.active_return import ActiveReturn
from src.performance_matrix.benchmark_relative_metrics.alpha import Alpha
from src.performance_matrix.benchmark_relative_metrics.beta import Beta
from src.performance_matrix.benchmark_relative_metrics.information_ratio import InformationRatio
from src.performance_matrix.benchmark_relative_metrics.tracking_rrror import TrackingError
from src.performance_matrix.return_matrix.percentage_change import PercentageChange
from src.utils.constants import GlobalStockData


@pytest.fixture
def stock_prices() -> pd.DataFrame:
    closes = np.array([100, 102, 101, 104, 105, 103, 107, 108, 109, 111], dtype=float)
    return pd.DataFrame({GlobalStockData.CLOSE: closes})


@pytest.fixture
def benchmark_prices() -> pd.DataFrame:
    closes = np.array([98, 99, 100, 101, 102, 101, 103, 104, 105, 106], dtype=float)
    return pd.DataFrame({GlobalStockData.CLOSE: closes})


class TestPercentageChange:
    def test_percentage_change_drops_na(self, stock_prices: pd.DataFrame):
        pct_change = PercentageChange(stock_prices).calculate()
        expected = stock_prices[GlobalStockData.CLOSE].pct_change().dropna()
        pd.testing.assert_series_equal(pct_change, expected)


class TestBeta:
    def test_beta_matches_covariance_ratio(self, stock_prices: pd.DataFrame, benchmark_prices: pd.DataFrame):
        beta = Beta(stock_prices, benchmark_prices).calculate()
        stock_returns = PercentageChange(stock_prices).calculate()
        benchmark_returns = PercentageChange(benchmark_prices).calculate()
        expected = stock_returns.cov(benchmark_returns) / benchmark_returns.var()
        assert beta == pytest.approx(expected)


class TestActiveReturn:
    def test_active_return_mean_difference(self, stock_prices: pd.DataFrame, benchmark_prices: pd.DataFrame):
        metric = ActiveReturn(stock_prices, benchmark_prices)
        result = metric.calculate()
        stock_returns = PercentageChange(stock_prices).calculate()
        benchmark_returns = PercentageChange(benchmark_prices).calculate()
        expected = stock_returns.mean() - benchmark_returns.mean()
        assert result == pytest.approx(expected)


class TestTrackingError:
    def test_tracking_error_standard_deviation(self, stock_prices: pd.DataFrame, benchmark_prices: pd.DataFrame):
        metric = TrackingError(stock_prices, benchmark_prices)
        result = metric.calculate()
        excess_returns = PercentageChange(stock_prices).calculate() - PercentageChange(benchmark_prices).calculate()
        expected = excess_returns.std()
        assert result == pytest.approx(expected)


class TestInformationRatio:
    def test_information_ratio(self, stock_prices: pd.DataFrame, benchmark_prices: pd.DataFrame):
        metric = InformationRatio(stock_prices, benchmark_prices)
        result = metric.calculate()
        excess_returns = PercentageChange(stock_prices).calculate() - PercentageChange(benchmark_prices).calculate()
        expected = excess_returns.mean() / excess_returns.std()
        assert result == pytest.approx(expected)


class TestAlpha:
    def test_alpha_uses_beta_and_excess_returns(self, stock_prices: pd.DataFrame, benchmark_prices: pd.DataFrame):
        metric = Alpha(stock_prices, benchmark_prices, risk_free_rate=0.01)
        result = metric.calculate()
        stock_returns = PercentageChange(stock_prices).calculate()
        benchmark_returns = PercentageChange(benchmark_prices).calculate()
        beta_value = Beta(stock_prices, benchmark_prices).calculate()
        expected = (stock_returns.mean() - 0.01) - beta_value * (benchmark_returns.mean() - 0.01)
        assert result == pytest.approx(expected)

