from tests.fixtures.test_data import DateRangeFixture, IndicatorsDataFixture, PerformanceDataFixture
from src.strategies.main import run_strategies


class TestRunStrategiesDataIntegrity:
    """Test data integrity and consistency in run_strategies results."""

    def test_all_results_have_consistent_date_range(self):
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

        for result in results:
            assert result["start_date"] == start_date
            assert result["end_date"] == end_date

    def test_unique_strategy_names_in_results(self):
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

        strategy_names = [result["strategy_name"] for result in results]

        assert len(strategy_names) == len(set(strategy_names))

    def test_no_duplicate_tickers_in_strategy_results(self):
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

        for result in results:
            tickers = result["tickers"]
            assert len(tickers) == len(set(tickers)), f"Duplicates found in {result['strategy_name']}"

