"""
Options Chain Module

Functions for fetching and analyzing options chains.
"""

import pandas as pd
import yfinance as yf
from typing import Optional, Dict, List
from datetime import datetime


def fetch_options_expiration_dates(ticker: str) -> List[str]:
    """
    Fetch available options expiration dates for a ticker.

    Args:
        ticker: Stock ticker symbol

    Returns:
        list: List of expiration date strings (YYYY-MM-DD format)
    """
    try:
        stock = yf.Ticker(ticker)
        return list(stock.options)
    except Exception as e:
        print(f"Error fetching expiration dates for {ticker}: {str(e)}")
        return []


def fetch_options_chain(
    ticker: str,
    expiration_date: Optional[str] = None
) -> Dict[str, pd.DataFrame]:
    """
    Fetch options chain for a given ticker and expiration date.

    Args:
        ticker: Stock ticker symbol
        expiration_date: Expiration date (YYYY-MM-DD). If None, uses nearest expiration.

    Returns:
        dict: Dictionary with 'calls' and 'puts' DataFrames
    """
    try:
        stock = yf.Ticker(ticker)

        # Get available expiration dates
        expirations = stock.options

        if not expirations:
            raise ValueError(f"No options data available for {ticker}")

        # Use provided expiration or default to nearest
        if expiration_date is None:
            expiration_date = expirations[0]
        elif expiration_date not in expirations:
            raise ValueError(f"Expiration date {expiration_date} not available. Available dates: {expirations}")

        # Fetch options chain
        options = stock.option_chain(expiration_date)

        return {
            'calls': options.calls,
            'puts': options.puts,
            'expiration_date': expiration_date,
            'ticker': ticker
        }

    except Exception as e:
        raise ValueError(f"Error fetching options chain for {ticker}: {str(e)}")


def filter_options_by_moneyness(
    options_df: pd.DataFrame,
    current_price: float,
    moneyness_range: float = 0.10
) -> pd.DataFrame:
    """
    Filter options to show only those near the current price (at-the-money).

    Args:
        options_df: Options DataFrame (calls or puts)
        current_price: Current stock price
        moneyness_range: Percentage range around current price (default: 10%)

    Returns:
        pd.DataFrame: Filtered options
    """
    lower_bound = current_price * (1 - moneyness_range)
    upper_bound = current_price * (1 + moneyness_range)

    filtered = options_df[
        (options_df['strike'] >= lower_bound) &
        (options_df['strike'] <= upper_bound)
    ]

    return filtered


def find_liquid_options(
    options_df: pd.DataFrame,
    min_volume: int = 100,
    min_open_interest: int = 500
) -> pd.DataFrame:
    """
    Filter options to show only liquid ones.

    Args:
        options_df: Options DataFrame
        min_volume: Minimum daily volume (default: 100)
        min_open_interest: Minimum open interest (default: 500)

    Returns:
        pd.DataFrame: Filtered liquid options
    """
    liquid = options_df[
        (options_df['volume'] >= min_volume) &
        (options_df['openInterest'] >= min_open_interest)
    ]

    return liquid


def calculate_option_spread(options_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate bid-ask spread for options.

    Args:
        options_df: Options DataFrame

    Returns:
        pd.DataFrame: Options with spread columns added
    """
    result_df = options_df.copy()

    result_df['spread'] = result_df['ask'] - result_df['bid']
    result_df['spread_pct'] = (result_df['spread'] / result_df['bid']) * 100

    return result_df


def get_option_summary_stats(options_chain: Dict[str, pd.DataFrame]) -> Dict:
    """
    Get summary statistics for an options chain.

    Args:
        options_chain: Dictionary with 'calls' and 'puts' DataFrames

    Returns:
        dict: Summary statistics
    """
    calls = options_chain['calls']
    puts = options_chain['puts']

    # Calculate put/call ratio
    total_call_volume = calls['volume'].sum()
    total_put_volume = puts['volume'].sum()
    put_call_ratio = total_put_volume / total_call_volume if total_call_volume > 0 else None

    # Find highest open interest
    max_call_oi = calls.loc[calls['openInterest'].idxmax()] if not calls.empty else None
    max_put_oi = puts.loc[puts['openInterest'].idxmax()] if not puts.empty else None

    return {
        'expiration_date': options_chain['expiration_date'],
        'total_call_volume': total_call_volume,
        'total_put_volume': total_put_volume,
        'put_call_ratio': put_call_ratio,
        'num_call_strikes': len(calls),
        'num_put_strikes': len(puts),
        'max_call_oi_strike': max_call_oi['strike'] if max_call_oi is not None else None,
        'max_put_oi_strike': max_put_oi['strike'] if max_put_oi is not None else None
    }


def display_options_chain(
    options_df: pd.DataFrame,
    option_type: str = 'calls'
) -> pd.DataFrame:
    """
    Format options chain for display.

    Args:
        options_df: Options DataFrame
        option_type: 'calls' or 'puts'

    Returns:
        pd.DataFrame: Formatted for display
    """
    display_cols = [
        'strike', 'lastPrice', 'bid', 'ask', 'volume',
        'openInterest', 'impliedVolatility'
    ]

    # Check which columns exist
    available_cols = [col for col in display_cols if col in options_df.columns]

    result = options_df[available_cols].copy()

    # Rename for clarity
    column_names = {
        'lastPrice': 'Last',
        'bid': 'Bid',
        'ask': 'Ask',
        'volume': 'Volume',
        'openInterest': 'OI',
        'impliedVolatility': 'IV'
    }

    result = result.rename(columns=column_names)

    # Format IV as percentage
    if 'IV' in result.columns:
        result['IV'] = result['IV'].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "N/A")

    return result
