from tests.fixtures.test_data import IndicatorsDataFixture, PerformanceDataFixture
from src.strategies.main import STRATEGY_DATA_MAPPING, StrategyFactory


class TestStrategyFactoryRunAllStrategies:
    """Test cases for running all strategies at once."""

    def test_run_all_strategies_returns_dict(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df(num_tickers=20)
        performance_df = PerformanceDataFixture.create_sample_performance_df(num_tickers=20)

        factory = StrategyFactory(indicators_df, performance_df, top_n=10)

        results = factory.run_all_strategies()

        assert isinstance(results, dict)
        assert len(results) > 0

    def test_run_all_strategies_includes_all_strategies(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df(num_tickers=20)
        performance_df = PerformanceDataFixture.create_sample_performance_df(num_tickers=20)

        factory = StrategyFactory(indicators_df, performance_df, top_n=10)

        results = factory.run_all_strategies()

        assert len(results) <= len(STRATEGY_DATA_MAPPING)

    def test_run_all_strategies_each_result_is_list(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df(num_tickers=20)
        performance_df = PerformanceDataFixture.create_sample_performance_df(num_tickers=20)

        factory = StrategyFactory(indicators_df, performance_df, top_n=10)

        results = factory.run_all_strategies()

        for strategy_name, tickers in results.items():
            assert isinstance(tickers, list), f"{strategy_name} did not return a list"
            assert all(isinstance(ticker, str) for ticker in tickers)

    def test_run_all_strategies_respects_top_n(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df(num_tickers=30)
        performance_df = PerformanceDataFixture.create_sample_performance_df(num_tickers=30)

        top_n = 8
        factory = StrategyFactory(indicators_df, performance_df, top_n=top_n)

        results = factory.run_all_strategies()

        for strategy_name, tickers in results.items():
            assert len(tickers) <= top_n, f"{strategy_name} returned {len(tickers)} tickers"

    def test_run_all_strategies_with_minimal_data(self):
        indicators_df = IndicatorsDataFixture.create_minimal_indicators_df()
        performance_df = PerformanceDataFixture.create_minimal_performance_df()

        factory = StrategyFactory(indicators_df, performance_df, top_n=2)

        results = factory.run_all_strategies()

        assert isinstance(results, dict)

    def test_run_all_strategies_handles_strategy_errors_gracefully(self):
        indicators_df = IndicatorsDataFixture.create_minimal_indicators_df()
        performance_df = PerformanceDataFixture.create_minimal_performance_df()

        factory = StrategyFactory(indicators_df, performance_df, top_n=5)

        results = factory.run_all_strategies()

        assert isinstance(results, dict)

    def test_run_all_strategies_with_different_top_n_values(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df(num_tickers=50)
        performance_df = PerformanceDataFixture.create_sample_performance_df(num_tickers=50)

        top_n_values = [5, 10, 15, 20]

        for top_n in top_n_values:
            factory = StrategyFactory(indicators_df, performance_df, top_n=top_n)
            results = factory.run_all_strategies()

            for tickers in results.values():
                assert len(tickers) <= top_n

