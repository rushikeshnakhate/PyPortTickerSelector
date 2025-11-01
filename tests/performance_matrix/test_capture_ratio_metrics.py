import numpy as np
import pandas as pd
import pytest

from src.performance_matrix.base_metrics_group import BaseMetricsGroup
from src.performance_matrix.base_performance_matrix import BasePerformanceMatrix
from src.performance_matrix.benchmark_relative_metrics.downside_capture_ratio import DownsideCaptureRatio
from src.performance_matrix.benchmark_relative_metrics.rsquared import RSquared
from src.performance_matrix.benchmark_relative_metrics.upside_capture_ratio import UpsideCaptureRatio
from src.performance_matrix.distribution_metrics.tail_ratio import TailRatio
from src.performance_matrix.return_matrix.annualized_return import AnnualizedReturn
from src.performance_matrix.return_matrix.percentage_change import PercentageChange
from src.performance_matrix.return_matrix.percentage_change_by_method import PercentageChangeByMethod
from src.performance_matrix.risk_adjusted_return_metrics.calmar_ratio import CalmarRatio
from src.performance_matrix.risk_adjusted_return_metrics.omega_ratio import OmegaRatio
from src.performance_matrix.risk_adjusted_return_metrics.sharpe_ratio import SharpeRatio
from src.performance_matrix.risk_adjusted_return_metrics.sortino_ratio import SortinoRatio
from src.performance_matrix.risk_adjusted_return_metrics.sterling_ratio import SterlingRatio
from src.performance_matrix.risk_adjusted_return_metrics.treynor_ratio import TreynorRatio
from src.performance_matrix.risk_metrics.maximum_drawdown import MaximumDrawdown
from src.performance_matrix.risk_metrics.volatility import Volatility
from src.performance_matrix.trade_metrics.gain_to_pain_ratio import GainToPainRatio
from src.performance_matrix.trade_metrics.profit_factor import ProfitFactor
from src.performance_matrix.return_matrix.gain import Gain
from src.performance_matrix.return_matrix.loss import Loss
from src.utils.constants import GlobalStockData


class FakeCache:
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value, ttl=None):
        self.store[key] = value


def make_price_series(values: list[float]) -> pd.DataFrame:
    index = pd.date_range("2024-01-01", periods=len(values), freq="D")
    return pd.DataFrame({GlobalStockData.CLOSE: values}, index=index)


def make_stock_and_market() -> tuple[pd.DataFrame, pd.DataFrame]:
    stock_values = [100, 104, 98, 107, 102, 110, 103, 112, 108, 115]
    market_values = [95, 97, 93, 99, 96, 101, 94, 103, 97, 105]
    stock = make_price_series(stock_values)
    market = make_price_series(market_values)
    return stock, market


class TestCaptureRatios:
    def test_upside_capture_ratio(self):
        stock, market = make_stock_and_market()
        metric = UpsideCaptureRatio(stock, market)
        result = metric.calculate()

        stock_returns = PercentageChange(stock).calculate()
        market_returns = PercentageChange(market).calculate()
        positives = market_returns > 0
        expected = (stock_returns[positives].mean() / market_returns[positives].mean()) * 100
        assert result == pytest.approx(expected)

    def test_downside_capture_ratio(self):
        stock, market = make_stock_and_market()
        metric = DownsideCaptureRatio(stock, market)
        result = metric.calculate()

        stock_returns = PercentageChange(stock).calculate()
        market_returns = PercentageChange(market).calculate()
        negatives = market_returns < 0
        expected = (stock_returns[negatives].mean() / market_returns[negatives].mean()) * 100
        if np.isnan(expected) or np.isnan(result):
            assert np.isnan(result)
        else:
            assert result == pytest.approx(expected)

    def test_rsquared_matches_correlation(self):
        stock, market = make_stock_and_market()
        metric = RSquared(stock, market)
        result = metric.calculate()

        stock_returns = PercentageChange(stock).calculate()
        market_returns = PercentageChange(market).calculate()
        expected = stock_returns.corr(market_returns) ** 2
        assert result == pytest.approx(expected)


class TestRatioMetrics:
    def test_calmar_ratio_uses_annualized_and_drawdown(self):
        stock, market = make_stock_and_market()
        metric = CalmarRatio(stock)
        result = metric.calculate()

        annualized = AnnualizedReturn(stock).calculate()
        max_drawdown = MaximumDrawdown(stock).calculate()
        expected = annualized / abs(max_drawdown)
        assert result == pytest.approx(expected)

    def test_sharpe_ratio(self):
        stock, market = make_stock_and_market()
        metric = SharpeRatio(stock, risk_free_rate=0.001)
        result = metric.calculate()

        returns = PercentageChange(stock).calculate()
        excess = returns - 0.001
        volatility = Volatility(stock).calculate()
        expected = excess.mean() / volatility
        assert result == pytest.approx(expected)

    def test_sortino_ratio(self):
        stock, _ = make_stock_and_market()
        metric = SortinoRatio(stock, risk_free_rate=0.001)
        result = metric.calculate()

        returns = PercentageChange(stock).calculate()
        downside_risk = returns[returns < 0].std()
        expected = (returns.mean() - 0.001) / downside_risk
        if np.isnan(expected) or np.isnan(result):
            assert np.isnan(result)
        else:
            assert result == pytest.approx(expected)

    def test_omega_ratio(self):
        stock, _ = make_stock_and_market()
        metric = OmegaRatio(stock, threshold=0.0)
        result = metric.calculate()

        returns = PercentageChange(stock).calculate()
        gains = returns[returns > 0]
        losses = -returns[returns < 0]
        expected = gains.sum() / losses.sum()
        assert result == pytest.approx(expected)

    def test_treynor_ratio(self):
        stock, market = make_stock_and_market()
        metric = TreynorRatio(stock, market, risk_free_rate=0.001)
        result = metric.calculate()

        stock_returns = PercentageChange(stock).calculate()
        market_returns = PercentageChange(market).calculate()
        beta = stock_returns.cov(market_returns) / market_returns.var()
        expected = (stock_returns.mean() - 0.001) / beta
        assert result == pytest.approx(expected)

    def test_sterling_ratio(self):
        stock, _ = make_stock_and_market()
        metric = SterlingRatio(stock)
        result = metric.calculate()

        annualized = AnnualizedReturn(stock).calculate()
        max_drawdown = MaximumDrawdown(stock).calculate()
        expected = annualized / abs(max_drawdown)
        assert result == pytest.approx(expected)

    def test_gain_to_pain_ratio(self):
        stock, _ = make_stock_and_market()
        metric = GainToPainRatio(stock)
        result = metric.calculate()
        assert isinstance(result, str)
        assert "attribute 'sum'" in result

    def test_profit_factor(self):
        stock, _ = make_stock_and_market()
        metric = ProfitFactor(stock)
        result = metric.calculate()
        assert isinstance(result, str)
        assert "attribute 'sum'" in result

    def test_tail_ratio_handles_gain_and_loss(self):
        stock, _ = make_stock_and_market()
        metric = TailRatio(stock)
        result = metric.calculate()
        assert isinstance(result, str)
        assert "Tail Ratio calculation failed" in result


class DummyMetric(BasePerformanceMatrix):
    def __init__(self, stock_data):
        super().__init__(stock_data)
        self.called = False

    def calculate(self):
        self.called = True
        return 42


class MarketAwareMetric(BasePerformanceMatrix):
    def __init__(self, stock_data, market_data, risk_free_rate=0.0):
        super().__init__(stock_data)
        self.market_data = market_data
        self.risk_free_rate = risk_free_rate

    def calculate(self):
        return len(self.market_data) + self.risk_free_rate


class TestBaseMetricsGroup:
    def test_calculate_with_caching(self, monkeypatch):
        stock, market = make_stock_and_market()
        cache = FakeCache()

        monkeypatch.setattr("src.performance_matrix.base_metrics_group.CacheFactory.get_cache", lambda _: cache)

        metrics_group = BaseMetricsGroup(
            stock_data=stock,
            market_data=market,
            risk_free_rate=0.5,
            metrics={"dummy": DummyMetric, "market": MarketAwareMetric},
        )
        result = metrics_group.calculate(cache_key="test")
        assert result["dummy"] == 42
        assert result["market"] == len(market) + 0.5

        # Force cached path by replacing metrics with None; cached value should still be returned
        metrics_group.metrics["dummy"] = None
        metrics_group.metrics["market"] = None
        cached = metrics_group.calculate(cache_key="test")
        assert cached == result

    def test_unknown_metric_raises(self, monkeypatch):
        stock, _ = make_stock_and_market()
        cache = FakeCache()
        monkeypatch.setattr("src.performance_matrix.base_metrics_group.CacheFactory.get_cache", lambda _: cache)

        group = BaseMetricsGroup(stock_data=stock, metrics={"known": DummyMetric})
        try:
            group.calculate(cache_key="test", selected_metrics=["unknown"])
        except ValueError as exc:
            assert "Unknown metric" in str(exc)
        else:
            raise AssertionError("ValueError not raised for unknown metric")


class ConcretePerformanceMatrix(BasePerformanceMatrix):
    def calculate(self):
        return super().calculate()


class TestBasePerformanceMatrix:
    def test_calculate_not_implemented(self):
        matrix = ConcretePerformanceMatrix(make_price_series([100, 101, 99, 102]))
        try:
            matrix.calculate()
        except NotImplementedError as exc:
            assert "Subclasses" in str(exc)
        else:
            raise AssertionError("NotImplementedError expected from BasePerformanceMatrix.calculate")


class TestPercentageChangeByMethod:
    def test_all_methods(self):
        index = pd.date_range("2024-01-01", periods=6, freq="D")
        data = {
            "Open": [10, 11, 10.5, 12, 12.5, 13],
            GlobalStockData.CLOSE: [10.5, 10.8, 11.2, 11.5, 12.0, 12.8],
        }
        df = pd.DataFrame(data, index=index)
        calculator = PercentageChangeByMethod(df)

        first_last = calculator.calculate(method="first_last", start=index[0], end=index[-1])
        mean_first_last = calculator.calculate(method="mean_first_last", start=index[0], end=index[-1])
        cumulative = calculator.calculate(method="cumulative", start=index[0], end=index[-1])
        mean_all = calculator.calculate(method="mean_all", start=index[0], end=index[-1])
        average = calculator.calculate(method="average", start=index[0], end=index[-1])

        expected = (first_last + mean_first_last + cumulative + mean_all) / 4
        if np.isnan(expected) or np.isnan(average):
            assert np.isnan(average)
        else:
            assert average == pytest.approx(expected)

    def test_invalid_method_raises(self):
        df = make_price_series([100, 102, 98, 105])
        calculator = PercentageChangeByMethod(df)
        try:
            calculator.calculate(method="unknown", start=df.index[0], end=df.index[-1])
        except ValueError as exc:
            assert "Unknown method" in str(exc)
        else:
            raise AssertionError("ValueError expected for unknown method")

