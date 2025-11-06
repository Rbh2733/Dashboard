"""
Breakout Scanner Module

Scans multiple tickers for pre-breakout signals and unusual momentum.

Scan criteria include:
- High relative volume
- RSI extremes (oversold/overbought)
- Moving average crossovers
- Proximity to 52-week highs
- Consolidation breakouts
- Volume surge detection
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from src.data.data_fetcher import fetch_historical_data, fetch_multiple_tickers
from src.analysis.technical import (
    calculate_sma,
    calculate_rsi,
    identify_golden_death_cross
)
from src.analysis.patterns import (
    detect_consolidation,
    calculate_52_week_high_low
)


def calculate_relative_volume(df: pd.DataFrame, period: int = 20) -> float:
    """
    Calculate relative volume (current volume vs average volume).

    Args:
        df: DataFrame with Volume data
        period: Lookback period for average volume (default: 20)

    Returns:
        float: Relative volume ratio (current / average)
    """
    if len(df) < period + 1:
        return None

    avg_volume = df['Volume'].iloc[:-1].tail(period).mean()
    current_volume = df['Volume'].iloc[-1]

    if avg_volume == 0:
        return None

    return current_volume / avg_volume


def check_volume_surge(df: pd.DataFrame, threshold: float = 2.0) -> bool:
    """
    Check if current volume shows a surge (significantly above average).

    Args:
        df: DataFrame with Volume data
        threshold: Minimum relative volume to consider a surge (default: 2.0)

    Returns:
        bool: True if volume surge detected
    """
    rel_vol = calculate_relative_volume(df)

    if rel_vol is None:
        return False

    return rel_vol >= threshold


def check_rsi_signal(df: pd.DataFrame, oversold: float = 30, overbought: float = 70) -> str:
    """
    Check RSI for oversold or overbought conditions.

    Args:
        df: DataFrame with Close prices
        oversold: RSI threshold for oversold (default: 30)
        overbought: RSI threshold for overbought (default: 70)

    Returns:
        str: 'oversold', 'overbought', or 'neutral'
    """
    rsi = calculate_rsi(df['Close'])

    if rsi.empty or pd.isna(rsi.iloc[-1]):
        return 'neutral'

    current_rsi = rsi.iloc[-1]

    if current_rsi < oversold:
        return 'oversold'
    elif current_rsi > overbought:
        return 'overbought'
    else:
        return 'neutral'


def check_ma_crossover(df: pd.DataFrame) -> str:
    """
    Check for moving average crossover signals.

    Args:
        df: DataFrame with Close prices

    Returns:
        str: 'golden_cross', 'death_cross', or 'none'
    """
    if len(df) < 200:
        return 'none'

    df_with_cross = identify_golden_death_cross(df)

    # Check last 5 days for crossovers
    recent = df_with_cross.tail(5)

    if recent['Golden_Cross'].any():
        return 'golden_cross'
    elif recent['Death_Cross'].any():
        return 'death_cross'
    else:
        return 'none'


def check_near_52w_high(df: pd.DataFrame, threshold: float = 5.0) -> bool:
    """
    Check if price is near 52-week high.

    Args:
        df: DataFrame with OHLC data
        threshold: Maximum percentage from 52w high (default: 5%)

    Returns:
        bool: True if within threshold of 52-week high
    """
    stats = calculate_52_week_high_low(df)
    return abs(stats['pct_from_high']) <= threshold


def check_consolidation_breakout(df: pd.DataFrame) -> Dict:
    """
    Check if stock is in consolidation or breaking out from consolidation.

    Args:
        df: DataFrame with OHLC data

    Returns:
        dict: Consolidation status and breakout information
    """
    consolidation = detect_consolidation(df, window=20)

    if len(consolidation) < 2:
        return {'in_consolidation': False, 'breaking_out': False}

    currently_consolidating = consolidation.iloc[-1]
    was_consolidating = consolidation.iloc[-10:-1].any() if len(consolidation) > 10 else False

    # Breakout: was consolidating recently, but not anymore
    # AND price is moving up with volume
    breaking_out = was_consolidating and not currently_consolidating

    if breaking_out and len(df) > 5:
        # Check if price is rising
        recent_close_change = ((df['Close'].iloc[-1] - df['Close'].iloc[-5]) / df['Close'].iloc[-5]) * 100
        breaking_out = breaking_out and recent_close_change > 2  # At least 2% up

    return {
        'in_consolidation': currently_consolidating,
        'breaking_out': breaking_out
    }


def scan_ticker(ticker: str, period: str = '1y', interval: str = '1d') -> Optional[Dict]:
    """
    Scan a single ticker for breakout signals.

    Args:
        ticker: Stock ticker symbol
        period: Data period (default: '1y')
        interval: Data interval (default: '1d')

    Returns:
        dict: Dictionary of signals and metrics, or None if error
    """
    try:
        df = fetch_historical_data(ticker, period=period, interval=interval)

        if df.empty or len(df) < 50:
            return None

        # Calculate all signals
        signals = {
            'ticker': ticker,
            'current_price': df['Close'].iloc[-1],
            'relative_volume': calculate_relative_volume(df),
            'volume_surge': check_volume_surge(df),
            'rsi_signal': check_rsi_signal(df),
            'ma_crossover': check_ma_crossover(df),
            'near_52w_high': check_near_52w_high(df),
            'consolidation': check_consolidation_breakout(df),
            'price_change_5d': ((df['Close'].iloc[-1] - df['Close'].iloc[-6]) / df['Close'].iloc[-6] * 100) if len(df) > 5 else None,
            'price_change_20d': ((df['Close'].iloc[-1] - df['Close'].iloc[-21]) / df['Close'].iloc[-21] * 100) if len(df) > 20 else None,
        }

        # Calculate RSI value
        rsi = calculate_rsi(df['Close'])
        if not rsi.empty:
            signals['rsi_value'] = rsi.iloc[-1]

        return signals

    except Exception as e:
        print(f"Error scanning {ticker}: {str(e)}")
        return None


def scan_multiple_tickers(
    tickers: List[str],
    period: str = '1y',
    interval: str = '1d',
    filters: Optional[Dict] = None
) -> pd.DataFrame:
    """
    Scan multiple tickers and return results as DataFrame.

    Args:
        tickers: List of ticker symbols
        period: Data period (default: '1y')
        interval: Data interval (default: '1d')
        filters: Optional filters to apply (e.g., {'volume_surge': True})

    Returns:
        pd.DataFrame: DataFrame of scan results
    """
    results = []

    for ticker in tickers:
        print(f"Scanning {ticker}...")
        signals = scan_ticker(ticker, period=period, interval=interval)

        if signals is not None:
            results.append(signals)

    if not results:
        return pd.DataFrame()

    df = pd.DataFrame(results)

    # Apply filters if provided
    if filters:
        for key, value in filters.items():
            if key in df.columns:
                if isinstance(value, bool):
                    df = df[df[key] == value]
                elif isinstance(value, (int, float)):
                    df = df[df[key] >= value]

    return df


def find_high_volume_movers(tickers: List[str], min_rel_volume: float = 2.0) -> pd.DataFrame:
    """
    Find tickers with high relative volume.

    Args:
        tickers: List of ticker symbols
        min_rel_volume: Minimum relative volume (default: 2.0)

    Returns:
        pd.DataFrame: Sorted by relative volume (descending)
    """
    df = scan_multiple_tickers(tickers)

    if df.empty:
        return df

    # Filter for high volume
    df = df[df['relative_volume'] >= min_rel_volume]

    # Sort by relative volume
    df = df.sort_values('relative_volume', ascending=False)

    return df


def find_oversold_stocks(tickers: List[str]) -> pd.DataFrame:
    """
    Find tickers with RSI indicating oversold conditions.

    Args:
        tickers: List of ticker symbols

    Returns:
        pd.DataFrame: Sorted by RSI (ascending)
    """
    df = scan_multiple_tickers(tickers)

    if df.empty:
        return df

    # Filter for oversold
    df = df[df['rsi_signal'] == 'oversold']

    # Sort by RSI value
    if 'rsi_value' in df.columns:
        df = df.sort_values('rsi_value', ascending=True)

    return df


def find_golden_cross_stocks(tickers: List[str]) -> pd.DataFrame:
    """
    Find tickers with recent golden cross signals.

    Args:
        tickers: List of ticker symbols

    Returns:
        pd.DataFrame: Stocks with golden cross signals
    """
    df = scan_multiple_tickers(tickers)

    if df.empty:
        return df

    # Filter for golden cross
    df = df[df['ma_crossover'] == 'golden_cross']

    return df


def find_breakout_candidates(tickers: List[str]) -> pd.DataFrame:
    """
    Find tickers showing potential breakout signals.

    Breakout criteria:
    - Breaking out of consolidation, OR
    - Near 52-week high with volume surge, OR
    - Golden cross with high volume

    Args:
        tickers: List of ticker symbols

    Returns:
        pd.DataFrame: Sorted by multiple breakout indicators
    """
    df = scan_multiple_tickers(tickers)

    if df.empty:
        return df

    # Extract consolidation breakout flag
    df['is_breaking_out'] = df['consolidation'].apply(lambda x: x.get('breaking_out', False) if isinstance(x, dict) else False)

    # Find breakout candidates
    breakout_candidates = df[
        (df['is_breaking_out']) |
        ((df['near_52w_high']) & (df['volume_surge'])) |
        ((df['ma_crossover'] == 'golden_cross') & (df['relative_volume'] > 1.5))
    ]

    # Calculate composite score
    breakout_candidates['breakout_score'] = (
        breakout_candidates['is_breaking_out'].astype(int) * 3 +
        breakout_candidates['near_52w_high'].astype(int) * 2 +
        breakout_candidates['volume_surge'].astype(int) * 2 +
        (breakout_candidates['ma_crossover'] == 'golden_cross').astype(int) * 2
    )

    # Sort by score
    breakout_candidates = breakout_candidates.sort_values('breakout_score', ascending=False)

    return breakout_candidates


# Common ticker lists for scanning
SP500_SAMPLE = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM',
    'V', 'JNJ', 'WMT', 'PG', 'MA', 'UNH', 'HD', 'DIS', 'BAC', 'XOM'
]

ETF_LIST = [
    'SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'ARKK', 'XLF',
    'XLE', 'XLK', 'XLV', 'XLP', 'XLI', 'XLY', 'XLC', 'XLRE'
]
