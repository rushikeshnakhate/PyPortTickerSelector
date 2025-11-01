from tests.fixtures.test_data import IndicatorsDataFixture, PerformanceDataFixture
from src.strategies.main import StrategyFactory


class TestStrategyFactoryEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_factory_with_top_n_zero(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df()
        performance_df = PerformanceDataFixture.create_sample_performance_df()

        factory = StrategyFactory(indicators_df, performance_df, top_n=0)

        assert factory.top_n == 0

    def test_factory_with_negative_top_n(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df()
        performance_df = PerformanceDataFixture.create_sample_performance_df()

        factory = StrategyFactory(indicators_df, performance_df, top_n=-5)

        assert factory.top_n == -5

    def test_factory_with_very_large_dataset(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df(num_tickers=100, num_days=365)
        performance_df = PerformanceDataFixture.create_sample_performance_df(num_tickers=100)

        factory = StrategyFactory(indicators_df, performance_df, top_n=20)

        result = factory.run_strategy("SharpeRatioStrategy")

        assert isinstance(result, list)
        assert len(result) <= 20

    def test_strategies_are_initialized_once(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df()
        performance_df = PerformanceDataFixture.create_sample_performance_df()

        factory = StrategyFactory(indicators_df, performance_df)

        strategy_ref = factory.strategies["SharpeRatioStrategy"]

        factory.run_strategy("SharpeRatioStrategy")

        assert factory.strategies["SharpeRatioStrategy"] is strategy_ref

