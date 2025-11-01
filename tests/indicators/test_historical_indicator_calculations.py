import numpy as np
import pandas as pd
import pytest

from src.indicators.historical_price_indicators.accumulation_distribution_line import ADLine
from src.indicators.historical_price_indicators.aroon import Aroon
from src.indicators.historical_price_indicators.chaikin_money_flow import ChaikinMoneyFlow
from src.indicators.historical_price_indicators.commodity_channel_index import CommodityChannelIndex
from src.indicators.historical_price_indicators.donchian_channel import DonchianChannel
from src.indicators.historical_price_indicators.ease_of_movement import EaseOfMovement
from src.indicators.historical_price_indicators.keltner_channel import KeltnerChannel
from src.indicators.historical_price_indicators.moving_average_convergence_divergence import (
    MovingAverageConvergenceDivergence,
)
from src.indicators.historical_price_indicators.on_balance_volume import OnBalanceVolume


@pytest.fixture
def ohlcv_frame() -> pd.DataFrame:
    index = pd.date_range("2024-01-01", periods=40, freq="D")
    close = np.linspace(100, 140, num=40)
    high = close + 2
    low = close - 2
    open_price = close - 1
    volume = np.linspace(1_000_000, 1_400_000, num=40)
    df = pd.DataFrame({
        "Open": open_price,
        "High": high,
        "Low": low,
        "Close": close,
        "Volume": volume,
    }, index=index)
    return df


class TestAccumulationDistributionLine:
    def test_ad_line_matches_manual_cumsum(self, ohlcv_frame: pd.DataFrame):
        indicator = ADLine(period=10)
        result = indicator.calculate(ohlcv_frame)

        money_flow_multiplier = ((ohlcv_frame["Close"] - ohlcv_frame["Low"]) -
                                 (ohlcv_frame["High"] - ohlcv_frame["Close"])) / (ohlcv_frame["High"] - ohlcv_frame["Low"])
        money_flow_volume = money_flow_multiplier * ohlcv_frame["Volume"]
        expected = money_flow_volume.cumsum().iloc[-1]
        assert result == pytest.approx(expected)

    def test_returns_none_for_empty_dataframe(self):
        indicator = ADLine(period=5)
        assert indicator.calculate(pd.DataFrame()) is None


class TestAroonIndicator:
    def test_aroon_up_down_values(self, ohlcv_frame: pd.DataFrame):
        indicator = Aroon(period=10)
        result = indicator.calculate(ohlcv_frame)

        rolling = ohlcv_frame["Close"].rolling(window=10)
        expected_up = ((rolling.apply(lambda x: x.argmax()) + 1) / 10 * 100).iloc[-1]
        expected_down = ((rolling.apply(lambda x: x.argmin()) + 1) / 10 * 100).iloc[-1]

        assert result["Aroon Up"] == pytest.approx(expected_up)
        assert result["Aroon Down"] == pytest.approx(expected_down)


class TestChaikinMoneyFlow:
    def test_cmf_matches_expected(self, ohlcv_frame: pd.DataFrame):
        indicator = ChaikinMoneyFlow(period=20)
        result = indicator.calculate(ohlcv_frame)

        mf = (
            (ohlcv_frame["Close"] - ohlcv_frame["Low"]) - (ohlcv_frame["High"] - ohlcv_frame["Close"])
        ) / (ohlcv_frame["High"] - ohlcv_frame["Low"])
        expected = (mf * ohlcv_frame["Volume"]).rolling(window=20).sum() / ohlcv_frame["Volume"].rolling(window=20).sum()
        assert result == pytest.approx(expected.iloc[-1])


class TestCommodityChannelIndex:
    def test_cci_matches_formula(self, ohlcv_frame: pd.DataFrame):
        indicator = CommodityChannelIndex(period=14)
        result = indicator.calculate(ohlcv_frame)

        tp = (ohlcv_frame["High"] + ohlcv_frame["Low"] + ohlcv_frame["Close"]) / 3
        sma = tp.rolling(window=14).mean()
        mad = tp.rolling(window=14).apply(lambda x: np.fabs(x - x.mean()).mean())
        expected = ((tp - sma) / (0.015 * mad)).iloc[-1]
        assert result == pytest.approx(expected)


class TestDonchianChannel:
    def test_returns_upper_and_lower_bands(self, ohlcv_frame: pd.DataFrame):
        indicator = DonchianChannel(period=14)
        result = indicator.calculate(ohlcv_frame)

        expected_upper = ohlcv_frame["High"].rolling(window=14).max().iloc[-1]
        expected_lower = ohlcv_frame["Low"].rolling(window=14).min().iloc[-1]
        assert result["Upper Band"] == pytest.approx(expected_upper)
        assert result["Lower Band"] == pytest.approx(expected_lower)


class TestEaseOfMovement:
    def test_eom_matches_rolling_mean(self, ohlcv_frame: pd.DataFrame):
        indicator = EaseOfMovement(period=10)
        result = indicator.calculate(ohlcv_frame)

        box_ratio = (ohlcv_frame["High"] - ohlcv_frame["Low"]) / (ohlcv_frame["Volume"] / 100000)
        expected = box_ratio.rolling(window=10).mean().iloc[-1]
        assert result == pytest.approx(expected)


class TestKeltnerChannel:
    def test_returns_upper_lower_tuple(self, ohlcv_frame: pd.DataFrame):
        indicator = KeltnerChannel(period=12, multiplier=1.5)
        upper, lower = indicator.calculate(ohlcv_frame)

        typical_price = (ohlcv_frame["High"] + ohlcv_frame["Low"] + ohlcv_frame["Close"]) / 3
        moving_avg = typical_price.rolling(window=12).mean()
        atr = ohlcv_frame["Close"].diff().abs().rolling(window=12).mean()
        expected_upper = moving_avg.iloc[-1] + (1.5 * atr.iloc[-1])
        expected_lower = moving_avg.iloc[-1] - (1.5 * atr.iloc[-1])

        assert upper == pytest.approx(expected_upper)
        assert lower == pytest.approx(expected_lower)


class TestMovingAverageConvergenceDivergence:
    def test_macd_returns_macd_and_signal(self, ohlcv_frame: pd.DataFrame):
        indicator = MovingAverageConvergenceDivergence(fast_period=5, slow_period=8, signal_period=4)
        result = indicator.calculate(ohlcv_frame["Close"])

        fast = ohlcv_frame["Close"].ewm(span=5, adjust=False).mean()
        slow = ohlcv_frame["Close"].ewm(span=8, adjust=False).mean()
        macd = fast - slow
        signal = macd.ewm(span=4, adjust=False).mean()
        assert result["MACD"] == pytest.approx(macd.iloc[-1])
        assert result["Signal Line"] == pytest.approx(signal.iloc[-1])

    def test_returns_none_for_empty_series(self):
        indicator = MovingAverageConvergenceDivergence()
        assert indicator.calculate(pd.Series(dtype=float)) is None


class TestOnBalanceVolume:
    def test_obv_cumulative_volume(self, ohlcv_frame: pd.DataFrame):
        indicator = OnBalanceVolume(period=10)
        result = indicator.calculate(ohlcv_frame)

        obv = np.where(ohlcv_frame["Close"] > ohlcv_frame["Close"].shift(1),
                       ohlcv_frame["Volume"],
                       np.where(ohlcv_frame["Close"] < ohlcv_frame["Close"].shift(1),
                                -ohlcv_frame["Volume"],
                                0))
        expected = obv.cumsum()[-1]
        assert result == pytest.approx(expected)

