"""
Pattern Recognition Module

Algorithmic identification of chart patterns and candlestick patterns.

Patterns included:
- Candlestick patterns (Doji, Engulfing, Hammer, Shooting Star)
- Chart patterns (Consolidation detection)
- Support and Resistance levels
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Optional, Dict


def identify_doji(df: pd.DataFrame, threshold: float = 0.1) -> pd.Series:
    """
    Identify Doji candlestick patterns.

    A Doji occurs when Open and Close are nearly equal,
    indicating indecision in the market.

    Args:
        df: DataFrame with OHLC data
        threshold: Maximum percentage difference between Open and Close (default: 0.1%)

    Returns:
        pd.Series: Boolean series indicating Doji candles
    """
    body_size = abs(df['Close'] - df['Open'])
    candle_range = df['High'] - df['Low']

    # Avoid division by zero
    candle_range = candle_range.replace(0, np.nan)

    body_percentage = (body_size / candle_range) * 100

    # Doji: body is very small relative to the range
    is_doji = body_percentage < threshold

    return is_doji


def identify_engulfing(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """
    Identify Bullish and Bearish Engulfing patterns.

    Bullish Engulfing: A large green candle completely engulfs the previous red candle.
    Bearish Engulfing: A large red candle completely engulfs the previous green candle.

    Args:
        df: DataFrame with OHLC data

    Returns:
        Tuple of (bullish_engulfing, bearish_engulfing) boolean series
    """
    # Current candle
    curr_open = df['Open']
    curr_close = df['Close']

    # Previous candle
    prev_open = df['Open'].shift(1)
    prev_close = df['Close'].shift(1)

    # Bullish Engulfing
    bullish_engulfing = (
        (prev_close < prev_open) &  # Previous candle is bearish
        (curr_close > curr_open) &  # Current candle is bullish
        (curr_open < prev_close) &  # Current opens below previous close
        (curr_close > prev_open)    # Current closes above previous open
    )

    # Bearish Engulfing
    bearish_engulfing = (
        (prev_close > prev_open) &  # Previous candle is bullish
        (curr_close < curr_open) &  # Current candle is bearish
        (curr_open > prev_close) &  # Current opens above previous close
        (curr_close < prev_open)    # Current closes below previous open
    )

    return bullish_engulfing, bearish_engulfing


def identify_hammer(df: pd.DataFrame, ratio: float = 2.0) -> pd.Series:
    """
    Identify Hammer candlestick pattern.

    A Hammer has a small body at the top and a long lower shadow,
    indicating potential bullish reversal.

    Args:
        df: DataFrame with OHLC data
        ratio: Minimum ratio of lower shadow to body (default: 2.0)

    Returns:
        pd.Series: Boolean series indicating Hammer candles
    """
    body = abs(df['Close'] - df['Open'])
    lower_shadow = df[['Open', 'Close']].min(axis=1) - df['Low']
    upper_shadow = df['High'] - df[['Open', 'Close']].max(axis=1)

    # Hammer criteria:
    # 1. Lower shadow is at least 2x the body
    # 2. Upper shadow is small (less than body)
    # 3. Body is small relative to range
    candle_range = df['High'] - df['Low']

    is_hammer = (
        (lower_shadow > ratio * body) &
        (upper_shadow < body) &
        (body < 0.3 * candle_range)
    )

    return is_hammer


def identify_shooting_star(df: pd.DataFrame, ratio: float = 2.0) -> pd.Series:
    """
    Identify Shooting Star candlestick pattern.

    A Shooting Star has a small body at the bottom and a long upper shadow,
    indicating potential bearish reversal.

    Args:
        df: DataFrame with OHLC data
        ratio: Minimum ratio of upper shadow to body (default: 2.0)

    Returns:
        pd.Series: Boolean series indicating Shooting Star candles
    """
    body = abs(df['Close'] - df['Open'])
    lower_shadow = df[['Open', 'Close']].min(axis=1) - df['Low']
    upper_shadow = df['High'] - df[['Open', 'Close']].max(axis=1)

    # Shooting Star criteria:
    # 1. Upper shadow is at least 2x the body
    # 2. Lower shadow is small (less than body)
    # 3. Body is small relative to range
    candle_range = df['High'] - df['Low']

    is_shooting_star = (
        (upper_shadow > ratio * body) &
        (lower_shadow < body) &
        (body < 0.3 * candle_range)
    )

    return is_shooting_star


def detect_consolidation(df: pd.DataFrame, window: int = 20, threshold: float = 0.05) -> pd.Series:
    """
    Detect consolidation periods (price moving sideways in a narrow range).

    Consolidation is detected when the price range over a window
    is small relative to the average price.

    Args:
        df: DataFrame with OHLC data
        window: Lookback window for consolidation detection (default: 20)
        threshold: Maximum price range as percentage of price (default: 5%)

    Returns:
        pd.Series: Boolean series indicating consolidation periods
    """
    # Calculate rolling high and low
    rolling_high = df['High'].rolling(window=window).max()
    rolling_low = df['Low'].rolling(window=window).min()

    # Calculate price range as percentage of average price
    avg_price = (rolling_high + rolling_low) / 2
    price_range_pct = ((rolling_high - rolling_low) / avg_price) * 100

    # Consolidation: price range is below threshold
    is_consolidating = price_range_pct < (threshold * 100)

    return is_consolidating


def find_support_resistance_levels(
    df: pd.DataFrame,
    window: int = 20,
    num_levels: int = 3
) -> Tuple[List[float], List[float]]:
    """
    Find support and resistance levels using local minima and maxima.

    This is a simplified approach. More sophisticated methods
    would use clustering algorithms.

    Args:
        df: DataFrame with OHLC data
        window: Window size for finding local extrema (default: 20)
        num_levels: Number of top support/resistance levels to return (default: 3)

    Returns:
        Tuple of (support_levels, resistance_levels) as lists of prices
    """
    # Find local minima (potential support)
    local_min = df['Low'][
        (df['Low'].shift(1) > df['Low']) &
        (df['Low'].shift(-1) > df['Low'])
    ]

    # Find local maxima (potential resistance)
    local_max = df['High'][
        (df['High'].shift(1) < df['High']) &
        (df['High'].shift(-1) < df['High'])
    ]

    # Get the most significant levels (by frequency/clustering)
    # For simplicity, just take the num_levels lowest and highest
    support_levels = sorted(local_min.nlargest(num_levels * 2).unique())[:num_levels]
    resistance_levels = sorted(local_max.nsmallest(num_levels * 2).unique(), reverse=True)[:num_levels]

    return support_levels.tolist(), resistance_levels.tolist()


def calculate_52_week_high_low(df: pd.DataFrame) -> Dict:
    """
    Calculate 52-week high and low, and current price position.

    Args:
        df: DataFrame with OHLC data (at least 1 year of data)

    Returns:
        dict: 52-week high, low, and percentage from high
    """
    if len(df) < 252:  # Less than 1 year of trading days
        lookback = len(df)
    else:
        lookback = 252

    recent_data = df.tail(lookback)

    high_52w = recent_data['High'].max()
    low_52w = recent_data['Low'].min()
    current_price = df['Close'].iloc[-1]

    pct_from_high = ((current_price - high_52w) / high_52w) * 100
    pct_from_low = ((current_price - low_52w) / low_52w) * 100

    return {
        '52_week_high': high_52w,
        '52_week_low': low_52w,
        'current_price': current_price,
        'pct_from_high': pct_from_high,
        'pct_from_low': pct_from_low,
        'near_52w_high': pct_from_high > -5  # Within 5% of high
    }


def add_all_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all pattern recognition indicators to a DataFrame.

    Args:
        df: DataFrame with OHLC data

    Returns:
        pd.DataFrame: Original DataFrame with added pattern columns
    """
    result_df = df.copy()

    # Candlestick patterns
    result_df['Doji'] = identify_doji(df)
    bullish_engulfing, bearish_engulfing = identify_engulfing(df)
    result_df['Bullish_Engulfing'] = bullish_engulfing
    result_df['Bearish_Engulfing'] = bearish_engulfing
    result_df['Hammer'] = identify_hammer(df)
    result_df['Shooting_Star'] = identify_shooting_star(df)

    # Chart patterns
    result_df['Consolidation'] = detect_consolidation(df)

    return result_df


def summarize_patterns(df: pd.DataFrame) -> Dict:
    """
    Summarize all detected patterns in the recent data.

    Args:
        df: DataFrame with OHLC data

    Returns:
        dict: Summary of patterns found in recent periods
    """
    # Add patterns
    df_with_patterns = add_all_patterns(df)

    # Look at last 30 days
    recent = df_with_patterns.tail(30)

    summary = {
        'doji_count': recent['Doji'].sum(),
        'bullish_engulfing_count': recent['Bullish_Engulfing'].sum(),
        'bearish_engulfing_count': recent['Bearish_Engulfing'].sum(),
        'hammer_count': recent['Hammer'].sum(),
        'shooting_star_count': recent['Shooting_Star'].sum(),
        'in_consolidation': recent['Consolidation'].iloc[-1] if len(recent) > 0 else False,
        'consolidation_days': recent['Consolidation'].sum()
    }

    # Add support/resistance levels
    support, resistance = find_support_resistance_levels(df)
    summary['support_levels'] = support
    summary['resistance_levels'] = resistance

    # Add 52-week stats
    summary['52_week_stats'] = calculate_52_week_high_low(df)

    return summary
