import logging

import pandas as pd
from tabulate import tabulate

from src.date_generator.date_range_generator import DateRangeGenerator
from src.indicators.main import get_indicator_bulk
from src.performance_matrix.main import get_performance_metrics_bulk
from src.service.main import fetch_market_and_price_data
from src.strategies.main import run_strategies
from src.utils.constants import GlobalConstant

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_indicators_and_performance(close_price, ticker_list, market_data, start_date, end_date):
    """Calculate indicators and performance metrics and return as DataFrames."""
    logger.info(f"Calculating indicators and performance for start_date={start_date}, end_date={end_date}")

    indicators_df = get_indicator_bulk(
        ticker_data_df=close_price, ticker_list=ticker_list, start_date=start_date, end_date=end_date
    )
    indicators_df["start_date"] = start_date
    indicators_df["end_date"] = end_date

    performance_df = get_performance_metrics_bulk(
        ticker_data_df=close_price, ticker_list=ticker_list, market_data=market_data,
        start_date=start_date, end_date=end_date
    )
    performance_df["start_date"] = start_date
    performance_df["end_date"] = end_date

    return indicators_df, performance_df


def run_pyport_ticker_selector(years,
                               months=None,
                               top_n_tickers=GlobalConstant.TOP_N_TICKERS,
                               tickers=None,
                               rebalancing_days=None,
                               rebalancing_months=None,
                               indicators=None,
                               performance_matrix=None,
                               strategies=None):
    """Main function to process date ranges and store results."""
    date_ranges = DateRangeGenerator(
        years=years,
        months=months,
        rebalancing_days=rebalancing_days,
        rebalancing_months=rebalancing_months
    ).get_date_range()

    results = []
    indicators_list = []
    performance_list = []

    for start_date, end_date in date_ranges:
        try:
            market_data, ticker_list, close_price = fetch_market_and_price_data(start_date, end_date, tickers)
            indicators_df, performance_df = calculate_indicators_and_performance(close_price, ticker_list, market_data,
                                                                                 start_date, end_date)
            strategy_results = run_strategies(indicators_df, performance_df, start_date, end_date, top_n_tickers)

            results.extend(strategy_results)
            indicators_list.append(indicators_df)
            performance_list.append(performance_df)

        except Exception as e:
            logger.error(f"Error={e}, start_date={start_date}, end_date={end_date}")

    # Convert lists to DataFrames
    results_df = pd.DataFrame(results)
    indicators_df_final = pd.concat(indicators_list, ignore_index=True)
    performance_df_final = pd.concat(performance_list, ignore_index=True)

    # Log the final DataFrames
    logger.info("\nFinal Strategy Results:\n{}".format(tabulate(results_df, headers='keys', tablefmt='psql')))
    logger.info("\nFinal Indicators DataFrame:\n{}".format(
        tabulate(indicators_df_final.head(), headers='keys', tablefmt='psql')))
    logger.info("\nFinal Performance DataFrame:\n{}".format(
        tabulate(performance_df_final.head(), headers='keys', tablefmt='psql')))

    # Save to CSV (optional)
    results_df.to_csv('strategy_results.csv', index=False)
    indicators_df_final.to_csv('indicators_results.csv', index=False)
    performance_df_final.to_csv('performance_results.csv', index=False)

    return results_df, indicators_df_final, performance_df_final


if __name__ == "__main__":
    run_pyport_ticker_selector(years=[2024], top_n_tickers=5)
