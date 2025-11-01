"""Test data fixtures for strategy factory unit tests."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Tuple

import numpy as np
import pandas as pd


class IndicatorsDataFixture:
    """Fixture class providing sample indicator data for testing."""

    @staticmethod
    def _generate_rng(seed: int = 42) -> np.random.Generator:
        return np.random.default_rng(seed)

    @classmethod
    def create_sample_indicators_df(cls, num_tickers: int = 20, num_days: int = 100) -> pd.DataFrame:
        """Create a sample indicators DataFrame with realistic trading indicators."""

        rng = cls._generate_rng()
        tickers = [f"TICKER{i:03d}" for i in range(num_tickers)]
        end_date = datetime.now()

        rows = []
        for idx, ticker in enumerate(tickers):
            close_price = rng.uniform(50, 500)
            bollinger_width = close_price * rng.uniform(0.05, 0.15)
            bollinger_upper = close_price + bollinger_width / 2
            bollinger_lower = close_price - bollinger_width / 2

            keltner_width = close_price * rng.uniform(0.04, 0.12)
            keltner_upper = close_price + keltner_width / 2
            keltner_lower = close_price - keltner_width / 2

            donchian_upper = close_price + rng.uniform(5, 15)
            donchian_lower = close_price - rng.uniform(5, 15)

            macd = rng.uniform(-3, 3)
            signal_line = macd - rng.uniform(-1, 1)

            date = end_date - timedelta(days=max(0, num_days - idx))

            row = {
                "Ticker": ticker,
                "Date": date,
                "Open": close_price * (1 + rng.uniform(-0.01, 0.01)),
                "High": close_price * (1 + rng.uniform(0, 0.02)),
                "Low": close_price * (1 - rng.uniform(0, 0.02)),
                "Close": close_price,
                "Volume": rng.integers(500_000, 5_000_000),
                "BollingerBands": {"Upper Band": bollinger_upper, "Lower Band": bollinger_lower},
                "ExponentialMovingAverage": close_price * (1 + rng.uniform(-0.03, 0.03)),
                "MovingAverage": close_price * (1 + rng.uniform(-0.04, 0.04)),
                "RelativeStrengthIndex": 20 + rng.uniform(-10, 60),
                "PriceRateOfChange": rng.uniform(-5, 5),
                "AccumulationDistributionLine": rng.uniform(-1_000_000, 1_000_000),
                "Aroon": {"Aroon Up": rng.uniform(0, 100), "Aroon Down": rng.uniform(0, 100)},
                "ChaikinMoneyFlow": rng.uniform(0.05, 0.5),
                "CommodityChannelIndex": rng.uniform(-250, 250),
                "DonchianChannel": {"Upper Band": donchian_upper, "Lower Band": donchian_lower},
                "EaseOfMovement": rng.uniform(-5, 5),
                "ForceIndex": rng.uniform(-100_000, 100_000),
                "KeltnerChannel": (keltner_upper, keltner_lower),
                "MovingAverageConvergenceDivergence": {"MACD": macd, "Signal Line": signal_line},
                "MoneyFlowIndex": rng.uniform(20, 80),
                "OnBalanceVolume": 1_000_000 + idx * 50_000 + rng.uniform(0, 10_000),
                "VortexIndicator": (rng.uniform(0.5, 1.5), rng.uniform(0.5, 1.5)),
                "WilliamsR": rng.uniform(-100, 0),
                "start_date": (date - timedelta(days=30)).strftime("%Y-%m-%d"),
                "end_date": date.strftime("%Y-%m-%d"),
            }

            # Derived helper columns for strategies that expect flattened names
            row["MovingAverageConvergenceDivergence.MACD"] = macd
            row["MovingAverageConvergenceDivergence.Signal Line"] = signal_line
            row["AroonUp"] = row["Aroon"]["Aroon Up"]
            row["BollingerLower"] = bollinger_lower
            row["BollingerWidth"] = bollinger_width
            row["DonchianLower"] = donchian_lower
            row["KeltnerLower"] = keltner_lower
            row["KeltnerWidth"] = keltner_width

            rows.append(row)

        df = pd.DataFrame(rows)
        return df

    @classmethod
    def create_minimal_indicators_df(cls) -> pd.DataFrame:
        """Create a minimal indicators DataFrame for edge case testing."""

        return cls.create_sample_indicators_df(num_tickers=3, num_days=3)

    @staticmethod
    def create_empty_indicators_df() -> pd.DataFrame:
        """Create an empty indicators DataFrame for edge case testing."""

        columns = [
            "Ticker",
            "Date",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "BollingerBands",
            "ExponentialMovingAverage",
            "MovingAverage",
            "RelativeStrengthIndex",
            "PriceRateOfChange",
            "AccumulationDistributionLine",
            "Aroon",
            "ChaikinMoneyFlow",
            "CommodityChannelIndex",
            "DonchianChannel",
            "EaseOfMovement",
            "ForceIndex",
            "KeltnerChannel",
            "MovingAverageConvergenceDivergence",
            "MoneyFlowIndex",
            "OnBalanceVolume",
            "VortexIndicator",
            "WilliamsR",
            "start_date",
            "end_date",
            "MovingAverageConvergenceDivergence.MACD",
            "MovingAverageConvergenceDivergence.Signal Line",
            "AroonUp",
            "BollingerLower",
            "BollingerWidth",
            "DonchianLower",
            "KeltnerLower",
            "KeltnerWidth",
        ]
        return pd.DataFrame(columns=columns)


class PerformanceDataFixture:
    """Fixture class providing sample performance metrics data for testing."""

    @staticmethod
    def _generate_rng(seed: int = 202) -> np.random.Generator:
        return np.random.default_rng(seed)

    @classmethod
    def create_sample_performance_df(cls, num_tickers: int = 20) -> pd.DataFrame:
        """Create a sample performance DataFrame with realistic performance metrics."""

        rng = cls._generate_rng()
        tickers = [f"TICKER{i:03d}" for i in range(num_tickers)]

        rows = []
        for idx, ticker in enumerate(tickers):
            volatility = rng.uniform(0.05, 0.6)
            max_drawdown = -rng.uniform(0.05, 0.6)
            conditional_var = -rng.uniform(0.02, 0.1)
            value_at_risk = -rng.uniform(0.01, 0.08)

            row = {
                "Ticker": ticker,
                "SharpeRatio": rng.uniform(-0.5, 3.0),
                "SortinoRatio": rng.uniform(-0.5, 3.5),
                "CalmarRatio": rng.uniform(-1.0, 4.0),
                "GainToPainRatio": rng.uniform(0.1, 3.0),
                "LossRate": rng.uniform(0.2, 0.7),
                "ProfitFactor": rng.uniform(0.5, 3.0),
                "WinRate": rng.uniform(0.3, 0.8),
                "AnnualizedReturn": rng.uniform(-0.2, 0.5),
                "AverageDailyReturn": rng.uniform(-0.003, 0.004),
                "CumulativeReturn": rng.uniform(-0.4, 1.0),
                "ConditionalValueAtRisk": conditional_var,
                "ValueAtRisk": value_at_risk,
                "MaximumDrawdown": max_drawdown,
                "UlcerIndex": rng.uniform(0.5, 20.0),
                "Volatility": volatility,
                "TotalTrades": rng.integers(20, 300),
                "AverageWin": rng.uniform(0.005, 0.05),
                "AverageLoss": -rng.uniform(0.005, 0.05),
                "GainToPain": rng.uniform(0.2, 2.5),
                "CreatedAt": datetime.now() - timedelta(days=idx),
            }
            rows.append(row)

        return pd.DataFrame(rows)

    @classmethod
    def create_minimal_performance_df(cls) -> pd.DataFrame:
        """Create a minimal performance DataFrame for edge case testing."""

        return cls.create_sample_performance_df(num_tickers=3)

    @staticmethod
    def create_empty_performance_df() -> pd.DataFrame:
        """Create an empty performance DataFrame for edge case testing."""

        columns = [
            "Ticker",
            "SharpeRatio",
            "SortinoRatio",
            "CalmarRatio",
            "GainToPainRatio",
            "LossRate",
            "ProfitFactor",
            "WinRate",
            "AnnualizedReturn",
            "AverageDailyReturn",
            "CumulativeReturn",
            "ConditionalValueAtRisk",
            "ValueAtRisk",
            "MaximumDrawdown",
            "UlcerIndex",
            "Volatility",
            "TotalTrades",
            "AverageWin",
            "AverageLoss",
            "GainToPain",
            "CreatedAt",
        ]
        return pd.DataFrame(columns=columns)

    @staticmethod
    def create_extreme_performance_df() -> pd.DataFrame:
        """Create performance DataFrame with extreme values for edge case testing."""

        data = {
            "Ticker": ["EXTREME001", "EXTREME002", "EXTREME003"],
            "SharpeRatio": [10.0, -5.0, 0.0],
            "SortinoRatio": [12.0, -4.0, 0.5],
            "CalmarRatio": [8.0, -3.0, 1.0],
            "GainToPainRatio": [5.0, 0.2, 1.5],
            "LossRate": [0.2, 0.8, 0.5],
            "ProfitFactor": [5.0, 0.3, 2.0],
            "WinRate": [0.9, 0.1, 0.6],
            "AnnualizedReturn": [1.5, -0.8, 0.1],
            "AverageDailyReturn": [0.01, -0.02, 0.0],
            "CumulativeReturn": [5.0, -0.9, 0.0],
            "ConditionalValueAtRisk": [-0.01, -0.5, -0.1],
            "ValueAtRisk": [-0.005, -0.3, -0.08],
            "MaximumDrawdown": [-0.02, -0.99, -0.4],
            "UlcerIndex": [0.5, 25.0, 10.0],
            "Volatility": [0.02, 1.2, 0.3],
            "TotalTrades": [500, 10, 150],
            "AverageWin": [0.1, 0.02, 0.03],
            "AverageLoss": [-0.02, -0.5, -0.05],
            "GainToPain": [6.0, 0.1, 1.2],
            "CreatedAt": [datetime.now()] * 3,
        }
        return pd.DataFrame(data)


class DateRangeFixture:
    """Fixture class providing sample date ranges for testing."""

    @staticmethod
    def create_standard_date_range() -> Tuple[str, str]:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

    @staticmethod
    def create_short_date_range() -> Tuple[str, str]:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

    @staticmethod
    def create_specific_date_range() -> Tuple[str, str]:
        return "2023-01-01", "2023-12-31"

