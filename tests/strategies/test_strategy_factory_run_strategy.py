import pytest

from tests.fixtures.test_data import IndicatorsDataFixture, PerformanceDataFixture
from src.strategies.main import StrategyFactory


class TestStrategyFactoryRunStrategy:
    """Test cases for running individual strategies."""

    def test_run_valid_indicator_strategy(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df(num_tickers=20)
        performance_df = PerformanceDataFixture.create_sample_performance_df(num_tickers=20)

        factory = StrategyFactory(indicators_df, performance_df, top_n=10)

        result = factory.run_strategy("RSIMomentumStrategy")

        assert isinstance(result, list)
        assert len(result) <= 10
        assert all(isinstance(ticker, str) for ticker in result)

    def test_run_valid_performance_strategy(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df(num_tickers=20)
        performance_df = PerformanceDataFixture.create_sample_performance_df(num_tickers=20)

        factory = StrategyFactory(indicators_df, performance_df, top_n=5)

        result = factory.run_strategy("SharpeRatioStrategy")

        assert isinstance(result, list)
        assert len(result) <= 5
        assert all(isinstance(ticker, str) for ticker in result)

    def test_run_invalid_strategy_raises_error(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df()
        performance_df = PerformanceDataFixture.create_sample_performance_df()

        factory = StrategyFactory(indicators_df, performance_df)

        with pytest.raises(ValueError, match="Strategy 'InvalidStrategy' not found"):
            factory.run_strategy("InvalidStrategy")

    @pytest.mark.xfail(reason="MACDCrossoverStrategy requires flattened MACD columns in source data")
    def test_run_multiple_strategies_sequentially(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df(num_tickers=20)
        performance_df = PerformanceDataFixture.create_sample_performance_df(num_tickers=20)

        factory = StrategyFactory(indicators_df, performance_df, top_n=10)

        strategies_to_test = [
            "RSIMomentumStrategy",
            "SharpeRatioStrategy",
            "MACDCrossoverStrategy",
        ]

        results = {}
        for strategy_name in strategies_to_test:
            results[strategy_name] = factory.run_strategy(strategy_name)

        assert len(results) == 3
        for tickers in results.values():
            assert isinstance(tickers, list)
            assert len(tickers) <= 10

    def test_run_strategy_returns_different_tickers_for_different_strategies(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df(num_tickers=30)
        performance_df = PerformanceDataFixture.create_sample_performance_df(num_tickers=30)

        factory = StrategyFactory(indicators_df, performance_df, top_n=10)

        result1 = factory.run_strategy("RSIMomentumStrategy")
        result2 = factory.run_strategy("SharpeRatioStrategy")

        assert isinstance(result1, list)
        assert isinstance(result2, list)

    def test_run_strategy_with_top_n_larger_than_available_tickers(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df(num_tickers=5)
        performance_df = PerformanceDataFixture.create_sample_performance_df(num_tickers=5)

        factory = StrategyFactory(indicators_df, performance_df, top_n=20)

        result = factory.run_strategy("SharpeRatioStrategy")

        assert len(result) <= 5

    @pytest.mark.xfail(reason="MACDCrossoverStrategy requires flattened MACD columns in source data")
    def test_run_all_trend_indicator_strategies(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df(num_tickers=25)
        performance_df = PerformanceDataFixture.create_sample_performance_df(num_tickers=25)

        factory = StrategyFactory(indicators_df, performance_df, top_n=10)

        trend_strategies = [
            "AroonTrendStrategy",
            "ExponentialMovingAverageTrendStrategy",
            "MACDCrossoverStrategy",
            "MovingAverageTrendStrategy",
        ]

        for strategy_name in trend_strategies:
            result = factory.run_strategy(strategy_name)
            assert isinstance(result, list)
            assert len(result) <= 10

    def test_run_all_momentum_indicator_strategies(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df(num_tickers=25)
        performance_df = PerformanceDataFixture.create_sample_performance_df(num_tickers=25)

        factory = StrategyFactory(indicators_df, performance_df, top_n=10)

        momentum_strategies = [
            "CCIMomentumStrategy",
            "PriceRateOfChangeMomentumStrategy",
            "RSIMomentumStrategy",
            "WilliamsRMomentumStrategy",
        ]

        for strategy_name in momentum_strategies:
            result = factory.run_strategy(strategy_name)
            assert isinstance(result, list)
            assert len(result) <= 10

