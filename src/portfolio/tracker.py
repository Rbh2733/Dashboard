"""
Portfolio Tracker Module

Functions for tracking portfolio performance, allocation, and metrics.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional


def calculate_portfolio_value(holdings: pd.DataFrame, current_prices: Dict[str, float]) -> pd.DataFrame:
    """
    Calculate current portfolio value and P/L.

    Args:
        holdings: DataFrame with columns: ticker, shares, purchase_price
        current_prices: Dictionary mapping ticker to current price

    Returns:
        pd.DataFrame: Holdings with added value and P/L columns
    """
    result_df = holdings.copy()

    # Add current prices
    result_df['current_price'] = result_df['ticker'].map(current_prices)

    # Calculate values
    result_df['cost_basis'] = result_df['shares'] * result_df['purchase_price']
    result_df['current_value'] = result_df['shares'] * result_df['current_price']
    result_df['gain_loss'] = result_df['current_value'] - result_df['cost_basis']
    result_df['gain_loss_pct'] = (result_df['gain_loss'] / result_df['cost_basis']) * 100

    return result_df


def calculate_portfolio_performance(holdings: pd.DataFrame) -> Dict:
    """
    Calculate overall portfolio performance metrics.

    Args:
        holdings: DataFrame with value and P/L columns

    Returns:
        dict: Portfolio performance metrics
    """
    total_cost = holdings['cost_basis'].sum()
    total_value = holdings['current_value'].sum()
    total_gain_loss = total_value - total_cost
    total_gain_loss_pct = (total_gain_loss / total_cost) * 100 if total_cost > 0 else 0

    return {
        'total_value': total_value,
        'total_cost': total_cost,
        'total_gain_loss': total_gain_loss,
        'total_gain_loss_pct': total_gain_loss_pct,
        'num_holdings': len(holdings)
    }


def calculate_allocation(holdings: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate portfolio allocation percentages.

    Args:
        holdings: DataFrame with current_value column

    Returns:
        pd.DataFrame: Holdings with allocation percentage
    """
    result_df = holdings.copy()
    total_value = result_df['current_value'].sum()

    if total_value > 0:
        result_df['allocation_pct'] = (result_df['current_value'] / total_value) * 100
    else:
        result_df['allocation_pct'] = 0

    return result_df


def calculate_portfolio_beta(
    holdings: pd.DataFrame,
    price_data: Dict[str, pd.DataFrame],
    benchmark_data: pd.DataFrame
) -> float:
    """
    Calculate portfolio beta relative to a benchmark.

    Beta measures volatility relative to the market.
    Beta > 1: More volatile than benchmark
    Beta < 1: Less volatile than benchmark
    Beta = 1: Same volatility as benchmark

    Args:
        holdings: DataFrame with ticker and allocation_pct
        price_data: Dictionary of price DataFrames for each ticker
        benchmark_data: DataFrame with benchmark prices

    Returns:
        float: Portfolio beta
    """
    # Calculate returns for benchmark
    benchmark_returns = benchmark_data['Close'].pct_change().dropna()

    weighted_beta = 0

    for _, holding in holdings.iterrows():
        ticker = holding['ticker']
        weight = holding['allocation_pct'] / 100

        if ticker in price_data and not price_data[ticker].empty:
            # Calculate returns for this stock
            stock_returns = price_data[ticker]['Close'].pct_change().dropna()

            # Align dates
            aligned_returns = pd.concat([stock_returns, benchmark_returns], axis=1, join='inner')
            aligned_returns.columns = ['stock', 'benchmark']

            if len(aligned_returns) > 20:  # Need enough data
                # Calculate beta: covariance(stock, benchmark) / variance(benchmark)
                covariance = aligned_returns['stock'].cov(aligned_returns['benchmark'])
                variance = aligned_returns['benchmark'].var()

                if variance > 0:
                    beta = covariance / variance
                    weighted_beta += beta * weight

    return weighted_beta


def compare_to_benchmark(
    portfolio_return: float,
    benchmark_returns: pd.Series
) -> Dict:
    """
    Compare portfolio performance to benchmark.

    Args:
        portfolio_return: Portfolio return percentage
        benchmark_returns: Series of benchmark returns

    Returns:
        dict: Comparison metrics
    """
    benchmark_total_return = ((1 + benchmark_returns).prod() - 1) * 100

    return {
        'portfolio_return': portfolio_return,
        'benchmark_return': benchmark_total_return,
        'alpha': portfolio_return - benchmark_total_return,
        'outperformance': portfolio_return > benchmark_total_return
    }


def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.02
) -> float:
    """
    Calculate Sharpe Ratio.

    Sharpe Ratio = (Return - Risk Free Rate) / Standard Deviation

    Higher Sharpe Ratio indicates better risk-adjusted returns.

    Args:
        returns: Series of returns
        risk_free_rate: Risk-free rate (default: 2% annual)

    Returns:
        float: Sharpe Ratio
    """
    if len(returns) < 2:
        return 0

    excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
    sharpe = excess_returns.mean() / excess_returns.std() if excess_returns.std() > 0 else 0

    # Annualize
    sharpe_annualized = sharpe * np.sqrt(252)

    return sharpe_annualized


def calculate_max_drawdown(prices: pd.Series) -> Tuple[float, str, str]:
    """
    Calculate maximum drawdown.

    Maximum drawdown is the largest peak-to-trough decline.

    Args:
        prices: Series of prices

    Returns:
        Tuple of (max_drawdown_pct, peak_date, trough_date)
    """
    cumulative = prices / prices.iloc[0]  # Normalize to 1
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max

    max_dd = drawdown.min()
    max_dd_idx = drawdown.idxmin()

    # Find the peak before the trough
    peak_idx = cumulative[:max_dd_idx].idxmax()

    return max_dd * 100, str(peak_idx), str(max_dd_idx)
