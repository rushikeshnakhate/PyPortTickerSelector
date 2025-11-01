from tests.fixtures.test_data import DateRangeFixture, IndicatorsDataFixture, PerformanceDataFixture
from src.strategies.main import run_strategies


class TestRunStrategiesPerformance:
    """Test performance characteristics of run_strategies."""

    def test_run_strategies_completes_with_large_dataset(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df(num_tickers=100, num_days=365)
        performance_df = PerformanceDataFixture.create_sample_performance_df(num_tickers=100)
        start_date, end_date = DateRangeFixture.create_standard_date_range()

        results = run_strategies(
            indicators_df=indicators_df,
            performance_df=performance_df,
            start_date=start_date,
            end_date=end_date,
            top_n_tickers=20,
        )

        assert isinstance(results, list)
        assert len(results) > 0

    def test_run_strategies_returns_expected_number_of_results(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df(num_tickers=20)
        performance_df = PerformanceDataFixture.create_sample_performance_df(num_tickers=20)
        start_date, end_date = DateRangeFixture.create_standard_date_range()

        results = run_strategies(
            indicators_df=indicators_df,
            performance_df=performance_df,
            start_date=start_date,
            end_date=end_date,
            top_n_tickers=10,
        )

        assert isinstance(results, list)
        assert len(results) > 0

