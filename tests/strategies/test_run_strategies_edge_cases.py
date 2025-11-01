from datetime import datetime, timedelta

from tests.fixtures.test_data import DateRangeFixture, IndicatorsDataFixture, PerformanceDataFixture
from src.strategies.main import run_strategies


class TestRunStrategiesEdgeCases:
    """Test edge cases and boundary conditions for run_strategies."""

    def test_run_strategies_with_top_n_zero(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df()
        performance_df = PerformanceDataFixture.create_sample_performance_df()
        start_date, end_date = DateRangeFixture.create_standard_date_range()

        results = run_strategies(
            indicators_df=indicators_df,
            performance_df=performance_df,
            start_date=start_date,
            end_date=end_date,
            top_n_tickers=0,
        )

        assert isinstance(results, list)

    def test_run_strategies_with_large_top_n(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df(num_tickers=10)
        performance_df = PerformanceDataFixture.create_sample_performance_df(num_tickers=10)
        start_date, end_date = DateRangeFixture.create_standard_date_range()

        results = run_strategies(
            indicators_df=indicators_df,
            performance_df=performance_df,
            start_date=start_date,
            end_date=end_date,
            top_n_tickers=100,
        )

        for result in results:
            assert len(result["tickers"]) <= 10

    def test_run_strategies_with_future_dates(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df()
        performance_df = PerformanceDataFixture.create_sample_performance_df()

        future_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")

        results = run_strategies(
            indicators_df=indicators_df,
            performance_df=performance_df,
            start_date=future_date,
            end_date=future_date,
            top_n_tickers=10,
        )

        for result in results:
            assert result["start_date"] == future_date

    def test_run_strategies_with_historical_dates(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df()
        performance_df = PerformanceDataFixture.create_sample_performance_df()

        start_date = "2020-01-01"
        end_date = "2020-12-31"

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

    def test_run_strategies_multiple_calls_consistency(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df(num_tickers=20)
        performance_df = PerformanceDataFixture.create_sample_performance_df(num_tickers=20)
        start_date, end_date = DateRangeFixture.create_standard_date_range()

        results1 = run_strategies(
            indicators_df=indicators_df,
            performance_df=performance_df,
            start_date=start_date,
            end_date=end_date,
            top_n_tickers=10,
        )

        results2 = run_strategies(
            indicators_df=indicators_df,
            performance_df=performance_df,
            start_date=start_date,
            end_date=end_date,
            top_n_tickers=10,
        )

        assert len(results1) == len(results2)
        assert {r["strategy_name"] for r in results1} == {r["strategy_name"] for r in results2}

