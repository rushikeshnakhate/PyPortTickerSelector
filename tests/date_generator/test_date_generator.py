from datetime import datetime

from src.date_generator.date_range_generator import DateRangeGenerator
from src.date_generator.rebalancing import Rebalancing


def test_generate_monthly_rebalancing():
    result = Rebalancing.generate_monthly(2024, 1)
    assert len(result) == 1
    start, end = result[0]
    assert start == datetime(2024, 1, 1).date()
    assert end == datetime(2024, 1, 31).date()


def test_generate_custom_days():
    result = Rebalancing.generate_custom_days(2024, 1, 10)
    assert all(isinstance(r, tuple) for r in result)
    assert result[0][0] == datetime(2024, 1, 1).date()
    # The first period should end on day 10
    assert result[0][1] == datetime(2024, 1, 10).date()


def test_date_range_generator_monthly():
    generator = DateRangeGenerator(years=2024, months=[1], rebalancing_months=1)
    result = generator.get_date_range()
    assert isinstance(result, list)
    assert len(result) == 12
    start, end = result[0]
    assert start.month == 1
    assert start.year == 2024
    assert start.day == 1
    assert end.day == 31


def test_date_range_generator_custom_days():
    generator = DateRangeGenerator(years=[2024], months=[1], rebalancing_days=7)
    result = generator.get_date_range()
    assert len(result) == 5  # 31 days / 7-day segments ≈ 5 ranges
    assert result[0][0] == datetime(2024, 1, 1).date()
    assert result[-1][1] == datetime(2024, 1, 31).date()


from src.date_generator.rebalancing_period import RebalancingPeriod


def test_rebalancing_period_values():
    assert RebalancingPeriod.DAILY.value == "daily"
    assert RebalancingPeriod.HALF_MONTHLY.value == "half_monthly"
    assert RebalancingPeriod.MONTHLY.value == "monthly"
    assert RebalancingPeriod.YEARLY.value == "yearly"


def test_rebalancing_period_enum_members():
    names = [p.name for p in RebalancingPeriod]
    values = [p.value for p in RebalancingPeriod]

    assert "DAILY" in names
    assert "monthly" in values
    assert len(RebalancingPeriod) == 4
