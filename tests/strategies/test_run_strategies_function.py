from datetime import datetime

from tests.fixtures.test_data import DateRangeFixture, IndicatorsDataFixture, PerformanceDataFixture
from src.strategies.main import run_strategies


class TestRunStrategiesFunction:
    """Test cases for run_strategies function."""

    def test_run_strategies_returns_list(self):
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

    def test_run_strategies_result_structure(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df(num_tickers=15)
        performance_df = PerformanceDataFixture.create_sample_performance_df(num_tickers=15)
        start_date, end_date = DateRangeFixture.create_short_date_range()

        results = run_strategies(
            indicators_df=indicators_df,
            performance_df=performance_df,
            start_date=start_date,
            end_date=end_date,
            top_n_tickers=5,
        )

        required_keys = {"start_date", "end_date", "strategy_name", "tickers"}

        for result in results:
            assert isinstance(result, dict)
            assert set(result.keys()) == required_keys
            assert result["start_date"] == start_date
            assert result["end_date"] == end_date
            assert isinstance(result["strategy_name"], str)
            assert isinstance(result["tickers"], list)

    def test_run_strategies_with_different_date_ranges(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df(num_tickers=20)
        performance_df = PerformanceDataFixture.create_sample_performance_df(num_tickers=20)

        date_ranges = [
            DateRangeFixture.create_standard_date_range(),
            DateRangeFixture.create_short_date_range(),
            DateRangeFixture.create_specific_date_range(),
        ]

        for start_date, end_date in date_ranges:
            results = run_strategies(
                indicators_df=indicators_df,
                performance_df=performance_df,
                start_date=start_date,
                end_date=end_date,
                top_n_tickers=10,
            )

            assert isinstance(results, list)
            assert len(results) > 0
            for result in results:
                assert result["start_date"] == start_date
                assert result["end_date"] == end_date

    def test_run_strategies_with_various_top_n_values(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df(num_tickers=30)
        performance_df = PerformanceDataFixture.create_sample_performance_df(num_tickers=30)
        start_date, end_date = DateRangeFixture.create_standard_date_range()

        for top_n in [5, 10, 15, 20]:
            results = run_strategies(
                indicators_df=indicators_df,
                performance_df=performance_df,
                start_date=start_date,
                end_date=end_date,
                top_n_tickers=top_n,
            )

            for result in results:
                assert len(result["tickers"]) <= top_n

    def test_run_strategies_ticker_lists_are_valid(self):
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
            assert isinstance(tickers, list)
            for ticker in tickers:
                assert isinstance(ticker, str)
                assert ticker

    def test_run_strategies_with_minimal_data(self):
        indicators_df = IndicatorsDataFixture.create_minimal_indicators_df()
        performance_df = PerformanceDataFixture.create_minimal_performance_df()
        start_date, end_date = DateRangeFixture.create_short_date_range()

        results = run_strategies(
            indicators_df=indicators_df,
            performance_df=performance_df,
            start_date=start_date,
            end_date=end_date,
            top_n_tickers=2,
        )

        assert isinstance(results, list)
        assert len(results) >= 0

    def test_run_strategies_includes_all_strategy_types(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df(num_tickers=25)
        performance_df = PerformanceDataFixture.create_sample_performance_df(num_tickers=25)
        start_date, end_date = DateRangeFixture.create_standard_date_range()

        results = run_strategies(
            indicators_df=indicators_df,
            performance_df=performance_df,
            start_date=start_date,
            end_date=end_date,
            top_n_tickers=10,
        )

        strategy_names = [result["strategy_name"] for result in results]

        assert len(set(strategy_names)) > 1

    def test_run_strategies_with_same_start_and_end_date(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df()
        performance_df = PerformanceDataFixture.create_sample_performance_df()

        date = datetime.now().strftime("%Y-%m-%d")

        results = run_strategies(
            indicators_df=indicators_df,
            performance_df=performance_df,
            start_date=date,
            end_date=date,
            top_n_tickers=10,
        )

        for result in results:
            assert result["start_date"] == date
            assert result["end_date"] == date

    def test_run_strategies_date_format_preserved(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df()
        performance_df = PerformanceDataFixture.create_sample_performance_df()

        start_date = "2023-01-15"
        end_date = "2023-12-31"

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

