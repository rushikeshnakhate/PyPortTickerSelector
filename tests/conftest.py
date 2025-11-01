"""Shared pytest fixtures for strategy tests."""
import pytest

from tests.fixtures.test_data import (
    DateRangeFixture,
    IndicatorsDataFixture,
    PerformanceDataFixture,
)


@pytest.fixture
def sample_indicators_df():
    return IndicatorsDataFixture.create_sample_indicators_df(num_tickers=20)


@pytest.fixture
def sample_performance_df():
    return PerformanceDataFixture.create_sample_performance_df(num_tickers=20)


@pytest.fixture
def minimal_indicators_df():
    return IndicatorsDataFixture.create_minimal_indicators_df()


@pytest.fixture
def minimal_performance_df():
    return PerformanceDataFixture.create_minimal_performance_df()


@pytest.fixture
def empty_indicators_df():
    return IndicatorsDataFixture.create_empty_indicators_df()


@pytest.fixture
def empty_performance_df():
    return PerformanceDataFixture.create_empty_performance_df()


@pytest.fixture
def extreme_performance_df():
    return PerformanceDataFixture.create_extreme_performance_df()


@pytest.fixture
def standard_date_range():
    return DateRangeFixture.create_standard_date_range()


@pytest.fixture
def short_date_range():
    return DateRangeFixture.create_short_date_range()


@pytest.fixture
def specific_date_range():
    return DateRangeFixture.create_specific_date_range()


@pytest.fixture
def large_indicators_df():
    return IndicatorsDataFixture.create_sample_indicators_df(num_tickers=100, num_days=365)


@pytest.fixture
def large_performance_df():
    return PerformanceDataFixture.create_sample_performance_df(num_tickers=100)


@pytest.fixture
def top_n_default():
    return 15


@pytest.fixture
def top_n_small():
    return 5


@pytest.fixture
def top_n_large():
    return 50
