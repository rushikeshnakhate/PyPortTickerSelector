# PyPortTickerSelector - Developer Guide

Quick reference for API usage, async execution, logging, and caching.

---

## Installation & Setup
```bash
git clone https://github.com/rushikeshnakhate/PyPortTickerSelector.git
cd PyPortTickerSelector
./setup.sh        # Creates environment and installs dependencies
./run.sh          # Runs example (reproduces paper results)
```

---

## Quick Start
```python
from src.main import run_pyport_ticker_selector

# Basic usage - returns 3 DataFrames
results, indicators, performance = run_pyport_ticker_selector(
    years=[2024],
    top_n_tickers=5
)
```

**Output:**
- `results`: Selected tickers per strategy
- `indicators`: 30+ technical indicators (RSI, MACD, Bollinger, etc.)
- `performance`: 25+ metrics (Sharpe, Sortino, Alpha, etc.)

---

## API Reference

### Main Function
```python
run_pyport_ticker_selector(
    years=[2024],                    # Required: Years to analyze
    tickers=None,                    # Optional: Stock list (None = all NSE)
    top_n_tickers=15,                # Number of stocks to select
    rebalancing_months=1,            # Monthly rebalancing
    rebalancing_days=None,           # Or daily (1-31)
    indicators=None,                 # List of indicators (None = all 30+)
    performance_matrix=None,         # List of metrics (None = all 25+)
    strategies=None                  # List of strategies (None = all 30+)
)
```

### Module APIs

#### 1. Date Range Generator
```python
from src.date_generator.date_range_generator import DateRangeGenerator

generator = DateRangeGenerator(years=2024, rebalancing_months=1)
date_ranges = generator.get_date_range()
# Returns: [(start_date, end_date), ...]
```

#### 2. Data Fetcher (Sync)
```python
from src.service.data_fetcher import DataFetcher

fetcher = DataFetcher()
df = fetcher.get_close_price_service(
    ticker='AAPL',
    start_date='2024-01-01',
    end_date='2024-12-31'
)
# Returns: DataFrame with OHLCV data
```

#### 3. Indicators
```python
from src.indicators.indicator_factory import IndicatorFactory

factory = IndicatorFactory(period=14)
indicators = factory.calculate_all_indicators(
    ticker_data_df=price_data,
    ticker='AAPL',
    start_date='2024-01-01',
    end_date='2024-12-31'
)
# Returns: DataFrame with RSI, MACD, Bollinger, EMA, etc.
```

#### 4. Performance Metrics
```python
from src.performance_matrix.main import get_performance_metrics_bulk

metrics = get_performance_metrics_bulk(
    ticker_data_df=price_data,
    ticker_list=['AAPL', 'GOOGL'],
    market_data=benchmark_data,
    start_date='2024-01-01',
    end_date='2024-12-31'
)
# Returns: DataFrame with Sharpe, Sortino, Alpha, Beta, etc.
```

#### 5. Strategies
```python
from src.strategies.strategy_factory import StrategyFactory

factory = StrategyFactory(indicators_df, performance_df, top_n=5)
selected = factory.apply_strategy('RSIMomentumStrategy')
# Returns: List of top N ticker symbols
```

---

## Asynchronous Execution

**Automatically enabled** for large datasets - no code changes needed.

### How It Works
```python
# Sequential (slow): 1000 stocks × 2s each = 2000s
# Parallel (fast): 1000 stocks fetched together = ~50s
# Speedup: 40×

# Library automatically uses async when processing multiple tickers
results = run_pyport_ticker_selector(
    years=[2024],
    tickers=list_of_1000_stocks  # Fetched in parallel automatically
)
```

### Manual Async Usage
```python
import asyncio
from src.service.data_fetcher import DataFetcher

async def fetch_parallel():
    fetcher = DataFetcher()
    tasks = [
        fetcher.get_close_price_service_async(
            ticker=t, start_date='2024-01-01', end_date='2024-12-31'
        )
        for t in ['AAPL', 'GOOGL', 'MSFT', 'AMZN']
    ]
    results = await asyncio.gather(*tasks)
    return results

data = asyncio.run(fetch_parallel())
```

**When to use:** Large stock lists (100+ tickers), custom workflows

---

## Caching System

**Achieves 87-91% hit rate = 8-12× speedup**

### Three Cache Backends

#### Pandas Cache (Default - Fast)
```python
from src.cache.cache_factory import CacheFactory
from src.utils.constants import CacheType

cache = CacheFactory.get_cache(CacheType.PANDAS)
cache.set("key", data, ttl=3600)  # Store 1 hour
data = cache.get("key")            # Retrieve
exists = cache.exists("key")       # Check
```

#### Redis Cache (Distributed)
```python
# Requires: redis-server running
cache = CacheFactory.get_cache(CacheType.REDIS)
cache.set("shared_key", data, ttl=7200)  # 2 hours
```

#### SQLite Cache (Persistent)
```python
cache = CacheFactory.get_cache(CacheType.SQLITE)
cache.set("historical", data, ttl=86400)  # 24 hours (persists across runs)
```

### Cache Operations
```python
# Clear cache
cache.clear()

# Check statistics
print(f"Hit rate: {cache.hit_rate()}%")
```

**First run:** Downloads all data (slow)  
**Second run:** Uses cache (fast - 9× speedup)

---

## Logging System

### Enable Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,  # or DEBUG, WARNING, ERROR
    format='%(asctime)s - %(levelname)s - %(message)s'
)

results = run_pyport_ticker_selector(years=[2024])
```

### Log Levels

**INFO:** Progress updates
```
INFO: Calculating indicators for AAPL (2024-01-01 to 2024-12-31)
INFO: Cache hit for AAPL close prices
INFO: Processing 100 tickers with RSI strategy
```

**WARNING:** Data issues
```
WARNING: MovingAverage: not enough data for stock len(data)=5
WARNING: Ticker XYZ skipped - insufficient data
```

**ERROR:** Failures
```
ERROR: Failed to fetch data for ABC: Network timeout
ERROR: MACD calculation error: Cannot aggregate non-numeric type
```

### Save Logs to File
```python
logging.basicConfig(
    level=logging.INFO,
    filename='pyport.log',
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

---

## Module Connectivity

**Data Flow:**
1. **DateRangeGenerator** → Creates rebalancing periods
2. **DataFetcher** → Downloads stock prices (Yahoo Finance)
3. **PyKeyCache** → Intercepts requests, returns cached data if available
4. **IndicatorFactory** → Calculates 30+ technical indicators
5. **PerformanceMetrics** → Calculates 25+ risk/return metrics
6. **StrategyFactory** → Ranks stocks, selects top N
7. **Logging** → Records all operations (runs across all modules)
8. **Output** → Returns DataFrames + saves CSV files

**Key Integration Points:**
- All data requests go through cache layer
- Async used automatically for multi-ticker operations
- Logging captures operations from all modules
- Each module outputs DataFrames that feed next module

---

## Custom Components

### Add Custom Indicator
```python
# File: src/indicators/custom_indicators.py
class MyIndicator:
    def calculate(self, data):
        return data['Close'].rolling(20).mean().iloc[-1]

# Register in indicator_factory.py
INDICATOR_MAP['MyIndicator'] = MyIndicator
```

### Add Custom Metric
```python
# File: src/performance_matrix/custom_metrics.py
class MyMetric:
    def calculate(self, returns):
        return returns.mean() / returns.std()

# Register in performance_factory.py
METRIC_MAP['MyMetric'] = MyMetric
```

### Add Custom Strategy
```python
# File: src/strategies/custom_strategies.py
class MyStrategy:
    def select(self):
        # Your selection logic
        return top_tickers

# Register in strategy_factory.py
STRATEGY_MAP['MyStrategy'] = MyStrategy
```

---

## Examples

### Example 1: Custom Stock List
```python
results, indicators, performance = run_pyport_ticker_selector(
    years=[2024],
    tickers=['RELIANCE.NS', 'TCS.NS', 'INFY.NS'],
    top_n_tickers=2
)
```

### Example 2: Specific Indicators & Strategies
```python
results, indicators, performance = run_pyport_ticker_selector(
    years=[2024],
    indicators=['RSI', 'BollingerBands', 'MACD'],
    performance_matrix=['SharpeRatio', 'SortinoRatio'],
    strategies=['RSIMomentumStrategy', 'SharpeRatioStrategy']
)
```

### Example 3: Weekly Rebalancing
```python
results, indicators, performance = run_pyport_ticker_selector(
    years=[2024],
    rebalancing_days=7,  # Every 7 days
    top_n_tickers=10
)
```

---

## Performance Tips

1. **Enable caching:** Automatically reduces API calls by 87-91%
2. **Use async:** Automatic for large datasets (40× faster)
3. **Select specific components:** Faster than calculating all 30+ indicators
4. **Batch process:** Split large datasets by year

---

## Troubleshooting

**Rate Limit (429 error):**
```python
import time
time.sleep(0.5)  # Add delay between requests
```

**Insufficient data warning:**
```python
# Use longer date range (need 14+ days for indicators)
results = run_pyport_ticker_selector(years=[2023, 2024])
```

**Clear cache:**
```python
from src.cache.cache_factory import CacheFactory
cache = CacheFactory.get_cache(CacheType.PANDAS)
cache.clear()
```

---

## Testing
```bash
./run_tests.sh    # Run all tests (90% coverage)
```

---

## Output Files

- `strategy_results.csv` - Top N tickers per strategy
- `indicators_results.csv` - All calculated indicators  
- `performance_results.csv` - All performance metrics
- `pyport.log` - Execution logs (if file logging enabled)

---

## Support

- GitHub: https://github.com/rushikeshnakhate/PyPortTickerSelector
- Issues: https://github.com/rushikeshnakhate/PyPortTickerSelector/issues
- Email: rushikeshnakhate@gmail.com
