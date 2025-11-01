import pytest

from tests.fixtures.test_data import IndicatorsDataFixture, PerformanceDataFixture
from src.strategies.main import STRATEGY_DATA_MAPPING, StrategyFactory


class TestStrategyFactoryInitialization:
    """Test cases for StrategyFactory initialization."""

    def test_init_with_valid_data(self, sample_indicators_df, sample_performance_df):
        factory = StrategyFactory(sample_indicators_df, sample_performance_df, top_n=5)

        assert factory.indicators_df is sample_indicators_df
        assert factory.performance_df is sample_performance_df
        assert factory.top_n == 5
        assert len(factory.strategies) == len(STRATEGY_DATA_MAPPING)

    def test_init_with_minimal_data(self, minimal_indicators_df, minimal_performance_df):
        factory = StrategyFactory(minimal_indicators_df, minimal_performance_df, top_n=2)

        assert factory.top_n == 2
        assert len(factory.strategies) == len(STRATEGY_DATA_MAPPING)

    def test_init_with_default_top_n(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df()
        performance_df = PerformanceDataFixture.create_sample_performance_df()

        factory = StrategyFactory(indicators_df, performance_df)

        assert factory.top_n == 15

    def test_init_with_large_top_n(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df(num_tickers=50)
        performance_df = PerformanceDataFixture.create_sample_performance_df(num_tickers=50)

        factory = StrategyFactory(indicators_df, performance_df, top_n=100)

        assert factory.top_n == 100

    def test_strategies_dictionary_contains_all_strategies(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df()
        performance_df = PerformanceDataFixture.create_sample_performance_df()

        factory = StrategyFactory(indicators_df, performance_df)

        assert set(factory.strategies.keys()) == set(STRATEGY_DATA_MAPPING.keys())

    def test_indicator_based_strategies_use_indicators_df(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df()
        performance_df = PerformanceDataFixture.create_sample_performance_df()

        factory = StrategyFactory(indicators_df, performance_df, top_n=10)

        indicator_strategies = [
            "AroonTrendStrategy",
            "RSIMomentumStrategy",
            "MACDCrossoverStrategy",
        ]

        for strategy_name in indicator_strategies:
            assert strategy_name in factory.strategies
            assert factory.strategies[strategy_name].df is indicators_df

    def test_performance_based_strategies_use_performance_df(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df()
        performance_df = PerformanceDataFixture.create_sample_performance_df()

        factory = StrategyFactory(indicators_df, performance_df, top_n=10)

        performance_strategies = [
            "SharpeRatioStrategy",
            "CalmarRatioStrategy",
            "MaximumDrawdownStrategy",
        ]

        for strategy_name in performance_strategies:
            assert strategy_name in factory.strategies
            assert factory.strategies[strategy_name].df is performance_df

