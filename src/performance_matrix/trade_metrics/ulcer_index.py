import numpy as np

from src.performance_matrix.base_performance_matrix import BasePerformanceMatrix
from src.performance_matrix.return_matrix.percentage_change import PercentageChange


class UlcerIndex(BasePerformanceMatrix):
    def calculate(self):
        cumulative_returns = (1 + PercentageChange(self.stock_data).calculate()).cumprod()
        peak = cumulative_returns.expanding(min_periods=1).max()
        drawdown = (cumulative_returns - peak) / peak
        return np.sqrt((drawdown ** 2).mean())
