from tests.fixtures.test_data import IndicatorsDataFixture, PerformanceDataFixture
from src.strategies.main import STRATEGY_DATA_MAPPING, StrategyFactory


class TestStrategyDataMapping:
    """Test cases for STRATEGY_DATA_MAPPING constant."""

    def test_strategy_data_mapping_exists(self):
        assert STRATEGY_DATA_MAPPING
        assert isinstance(STRATEGY_DATA_MAPPING, dict)

    def test_strategy_data_mapping_has_valid_values(self):
        valid_values = {"indicator", "performance"}

        for strategy_name, data_type in STRATEGY_DATA_MAPPING.items():
            assert data_type in valid_values, f"{strategy_name} has invalid data type: {data_type}"

    def test_strategy_data_mapping_covers_all_strategies(self):
        indicator_strategies = [k for k, v in STRATEGY_DATA_MAPPING.items() if v == "indicator"]
        performance_strategies = [k for k, v in STRATEGY_DATA_MAPPING.items() if v == "performance"]

        assert len(indicator_strategies) > 0
        assert len(performance_strategies) > 0

    def test_all_strategies_in_factory_are_in_mapping(self):
        indicators_df = IndicatorsDataFixture.create_sample_indicators_df()
        performance_df = PerformanceDataFixture.create_sample_performance_df()

        factory = StrategyFactory(indicators_df, performance_df)

        for strategy_name in factory.strategies.keys():
            assert strategy_name in STRATEGY_DATA_MAPPING

