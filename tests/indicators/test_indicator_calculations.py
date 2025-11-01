import numpy as np
import pandas as pd
import pytest

from src.indicators.close_price_indicators.bollinger_bands import BollingerBands
from src.indicators.close_price_indicators.exponential_moving_average import ExponentialMovingAverage
from src.indicators.close_price_indicators.force_index import ForceIndex
from src.indicators.close_price_indicators.money_flow_index import MoneyFlowIndex
from src.indicators.close_price_indicators.moving_average import MovingAverageIndicator
from src.indicators.close_price_indicators.price_rate_of_change import PriceRateOfChange
from src.indicators.close_price_indicators.relative_strength_index import RelativeStrengthIndex
from src.indicators.close_price_indicators.vortex_indicator import VortexIndicator
from src.indicators.close_price_indicators.williams_percentage_R import WilliamsR
from src.indicators.historical_price_indicators.average_true_range import AverageTrueRange


@pytest.fixture
def price_series() -> pd.Series:
    values = np.array([100, 102, 101, 103, 104, 100, 102, 105, 103, 107, 106, 109, 108, 110, 111, 109, 112, 113, 111, 114],
                      dtype=float)
    return pd.Series(values, name="Close")


@pytest.fixture
def ohlcv_frame(price_series: pd.Series) -> pd.DataFrame:
    df = pd.DataFrame({
        "Close": price_series,
        "High": price_series + 1.5,
        "Low": price_series - 1.5,
        "Volume": np.linspace(100_000, 300_000, len(price_series))
    })
    return df


class TestMovingAverageIndicator:
    def test_calculates_simple_average(self, price_series: pd.Series):
        indicator = MovingAverageIndicator(period=5)
        result = indicator.calculate(price_series)
        expected = price_series.iloc[-5:].mean()
        assert result == pytest.approx(expected)

    def test_returns_none_when_not_enough_data(self):
        indicator = MovingAverageIndicator(period=5)
        short_series = pd.Series([1, 2])
        assert indicator.calculate(short_series) is None


class TestExponentialMovingAverage:
    def test_ema_matches_pandas(self, price_series: pd.Series):
        indicator = ExponentialMovingAverage(period=10)
        result = indicator.calculate(price_series)
        expected = price_series.ewm(span=10, adjust=False).mean().iloc[-1]
        assert result == pytest.approx(expected)

    def test_returns_none_for_empty_series(self):
        indicator = ExponentialMovingAverage(period=5)
        empty_series = pd.Series(dtype=float)
        assert indicator.calculate(empty_series) is None


class TestPriceRateOfChange:
    def test_rate_of_change(self):
        data = pd.Series([10, 12, 15, 18, 21], dtype=float)
        indicator = PriceRateOfChange(period=2)
        result = indicator.calculate(data)
        expected = ((data.iloc[-1] - data.shift(2).iloc[-1]) / data.shift(2).iloc[-1]) * 100
        assert result == pytest.approx(expected)

    def test_returns_none_for_empty_series(self):
        indicator = PriceRateOfChange(period=3)
        assert indicator.calculate(pd.Series(dtype=float)) is None


class TestRelativeStrengthIndex:
    def test_rsi_computation(self, price_series: pd.Series):
        indicator = RelativeStrengthIndex(period=5)
        result = indicator.calculate(price_series)

        delta = price_series.diff()
        gain = delta.where(delta > 0, 0).rolling(window=5).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=5).mean()
        rsi_expected = 100 - (100 / (1 + (gain / loss)))
        assert result == pytest.approx(rsi_expected.iloc[-1], nan_ok=True)

    def test_returns_none_for_empty_series(self):
        indicator = RelativeStrengthIndex(period=5)
        assert indicator.calculate(pd.Series(dtype=float)) is None


class TestBollingerBands:
    def test_returns_upper_and_lower_band(self, price_series: pd.Series):
        indicator = BollingerBands(period=5, num_std=2)
        bands = indicator.calculate(price_series)
        rolling_mean = price_series.rolling(window=5).mean()
        rolling_std = price_series.rolling(window=5).std()
        expected_upper = rolling_mean.iloc[-1] + (rolling_std.iloc[-1] * 2)
        expected_lower = rolling_mean.iloc[-1] - (rolling_std.iloc[-1] * 2)

        assert bands["Upper Band"] == pytest.approx(expected_upper)
        assert bands["Lower Band"] == pytest.approx(expected_lower)

    def test_returns_none_for_empty_series(self):
        indicator = BollingerBands(period=5)
        assert indicator.calculate(pd.Series(dtype=float)) is None


class TestForceIndex:
    def test_force_index_rolling_mean(self, ohlcv_frame: pd.DataFrame):
        indicator = ForceIndex(period=3)
        result = indicator.calculate(ohlcv_frame)
        diffs = ohlcv_frame["Close"].diff() * ohlcv_frame["Volume"]
        expected = diffs.rolling(window=3).mean().iloc[-1]
        assert result == pytest.approx(expected)

    def test_returns_none_for_empty_dataframe(self):
        indicator = ForceIndex(period=3)
        empty_df = pd.DataFrame(columns=["Close", "Volume"])
        assert indicator.calculate(empty_df) is None


class TestMoneyFlowIndex:
    def test_money_flow_index(self, ohlcv_frame: pd.DataFrame):
        indicator = MoneyFlowIndex(period=5)
        result = indicator.calculate(ohlcv_frame)

        typical_price = (ohlcv_frame["High"] + ohlcv_frame["Low"] + ohlcv_frame["Close"]) / 3
        money_flow = typical_price * ohlcv_frame["Volume"]
        money_flow_pos = money_flow.where(ohlcv_frame["Close"] > ohlcv_frame["Close"].shift(), 0)
        money_flow_neg = money_flow.where(ohlcv_frame["Close"] < ohlcv_frame["Close"].shift(), 0)
        mf_ratio = money_flow_pos.rolling(window=5).sum() / money_flow_neg.rolling(window=5).sum()
        expected = 100 - (100 / (1 + mf_ratio.iloc[-1]))

        assert result == pytest.approx(expected, nan_ok=True)

    def test_returns_none_for_empty_dataframe(self):
        indicator = MoneyFlowIndex(period=5)
        empty_df = pd.DataFrame(columns=["High", "Low", "Close", "Volume"])
        assert indicator.calculate(empty_df) is None


class TestVortexIndicator:
    def test_vortex_indicator(self, ohlcv_frame: pd.DataFrame):
        indicator = VortexIndicator(period=4)
        vi_plus, vi_minus = indicator.calculate(ohlcv_frame)

        tr = pd.concat([
            ohlcv_frame["High"] - ohlcv_frame["Low"],
            (ohlcv_frame["High"] - ohlcv_frame["Close"].shift()).abs(),
            (ohlcv_frame["Low"] - ohlcv_frame["Close"].shift()).abs()
        ], axis=1).max(axis=1)
        vm_plus = (ohlcv_frame["High"] - ohlcv_frame["High"].shift()).rolling(window=4).sum()
        vm_minus = (ohlcv_frame["Low"].shift() - ohlcv_frame["Low"]).rolling(window=4).sum()
        denominator = tr.rolling(window=4).sum().iloc[-1]

        expected_plus = vm_plus.iloc[-1] / denominator
        expected_minus = vm_minus.iloc[-1] / denominator

        assert vi_plus == pytest.approx(expected_plus, nan_ok=True)
        assert vi_minus == pytest.approx(expected_minus, nan_ok=True)

    def test_returns_none_for_empty_dataframe(self):
        indicator = VortexIndicator(period=3)
        empty_df = pd.DataFrame(columns=["High", "Low", "Close"])
        assert indicator.calculate(empty_df) is None


class TestWilliamsR:
    def test_williams_r(self, ohlcv_frame: pd.DataFrame):
        indicator = WilliamsR(period=5)
        result = indicator.calculate(ohlcv_frame)
        highest_high = ohlcv_frame["High"].rolling(window=5).max().iloc[-1]
        lowest_low = ohlcv_frame["Low"].rolling(window=5).min().iloc[-1]
        expected = -100 * ((highest_high - ohlcv_frame["Close"].iloc[-1]) / (highest_high - lowest_low))
        assert result == pytest.approx(expected)

    def test_returns_none_for_empty_dataframe(self):
        indicator = WilliamsR(period=5)
        empty_df = pd.DataFrame(columns=["High", "Low", "Close"])
        assert indicator.calculate(empty_df) is None


class TestAverageTrueRange:
    def test_average_true_range(self, ohlcv_frame: pd.DataFrame):
        indicator = AverageTrueRange(period=5)
        result = indicator.calculate(ohlcv_frame)

        high_low = ohlcv_frame["High"] - ohlcv_frame["Low"]
        high_close = (ohlcv_frame["High"] - ohlcv_frame["Close"].shift()).abs()
        low_close = (ohlcv_frame["Low"] - ohlcv_frame["Close"].shift()).abs()
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        expected = true_range.rolling(window=5).mean().iloc[-1]
        assert result == pytest.approx(expected, nan_ok=True)

    def test_returns_none_for_empty_dataframe(self):
        indicator = AverageTrueRange(period=5)
        assert indicator.calculate(pd.DataFrame()) is None

