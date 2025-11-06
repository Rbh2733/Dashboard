"""
Technical Analysis Module

Implements common technical indicators from scratch using pandas and numpy.
All functions are well-documented with formulas and interpretations.

Indicators included:
- Moving Averages (SMA, EMA)
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- VWAP (Volume Weighted Average Price)
- OBV (On-Balance Volume)
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple


def calculate_sma(data: pd.Series, period: int) -> pd.Series:
    """
    Calculate Simple Moving Average (SMA).

    Formula: SMA = Sum of prices over period / period

    Args:
        data: Price series (typically Close prices)
        period: Number of periods for the moving average

    Returns:
        pd.Series: SMA values
    """
    return data.rolling(window=period).mean()


def calculate_ema(data: pd.Series, period: int) -> pd.Series:
    """
    Calculate Exponential Moving Average (EMA).

    EMA gives more weight to recent prices.
    Formula: EMA = (Price(t) * k) + (EMA(y) * (1 - k))
    where k = 2 / (period + 1)

    Args:
        data: Price series (typically Close prices)
        period: Number of periods for the moving average

    Returns:
        pd.Series: EMA values
    """
    return data.ewm(span=period, adjust=False).mean()


def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).

    RSI measures the magnitude of recent price changes to evaluate
    overbought or oversold conditions.

    Formula:
        RSI = 100 - (100 / (1 + RS))
        where RS = Average Gain / Average Loss over period

    Interpretation:
        - RSI > 70: Overbought (potential sell signal)
        - RSI < 30: Oversold (potential buy signal)

    Args:
        data: Price series (typically Close prices)
        period: Lookback period (default: 14)

    Returns:
        pd.Series: RSI values (0-100)
    """
    # Calculate price changes
    delta = data.diff()

    # Separate gains and losses
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)

    # Calculate average gain and loss
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_macd(
    data: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate MACD (Moving Average Convergence Divergence).

    MACD shows the relationship between two moving averages.

    Formula:
        MACD Line = EMA(fast) - EMA(slow)
        Signal Line = EMA(MACD, signal_period)
        Histogram = MACD Line - Signal Line

    Interpretation:
        - MACD crosses above signal: Bullish signal
        - MACD crosses below signal: Bearish signal
        - Histogram shows momentum strength

    Args:
        data: Price series (typically Close prices)
        fast_period: Fast EMA period (default: 12)
        slow_period: Slow EMA period (default: 26)
        signal_period: Signal line EMA period (default: 9)

    Returns:
        Tuple of (macd_line, signal_line, histogram)
    """
    # Calculate EMAs
    ema_fast = calculate_ema(data, fast_period)
    ema_slow = calculate_ema(data, slow_period)

    # Calculate MACD line
    macd_line = ema_fast - ema_slow

    # Calculate signal line
    signal_line = calculate_ema(macd_line, signal_period)

    # Calculate histogram
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


def calculate_bollinger_bands(
    data: pd.Series,
    period: int = 20,
    std_dev: float = 2.0
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate Bollinger Bands.

    Bollinger Bands consist of a middle band (SMA) and two outer bands
    at standard deviations away from the middle.

    Formula:
        Middle Band = SMA(period)
        Upper Band = Middle Band + (std_dev * standard deviation)
        Lower Band = Middle Band - (std_dev * standard deviation)

    Interpretation:
        - Price near upper band: Potentially overbought
        - Price near lower band: Potentially oversold
        - Bands squeeze: Low volatility (potential breakout coming)
        - Bands widen: High volatility

    Args:
        data: Price series (typically Close prices)
        period: Period for SMA (default: 20)
        std_dev: Number of standard deviations (default: 2.0)

    Returns:
        Tuple of (upper_band, middle_band, lower_band)
    """
    middle_band = calculate_sma(data, period)
    rolling_std = data.rolling(window=period).std()

    upper_band = middle_band + (rolling_std * std_dev)
    lower_band = middle_band - (rolling_std * std_dev)

    return upper_band, middle_band, lower_band


def calculate_vwap(df: pd.DataFrame) -> pd.Series:
    """
    Calculate Volume Weighted Average Price (VWAP).

    VWAP is the average price weighted by volume.

    Formula:
        VWAP = Cumulative(Price * Volume) / Cumulative(Volume)
        where Price = (High + Low + Close) / 3

    Interpretation:
        - Price > VWAP: Bullish (buying pressure)
        - Price < VWAP: Bearish (selling pressure)
        - Often used as a benchmark by institutions

    Args:
        df: DataFrame with columns: High, Low, Close, Volume

    Returns:
        pd.Series: VWAP values
    """
    # Calculate typical price
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3

    # Calculate VWAP
    vwap = (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()

    return vwap


def calculate_obv(df: pd.DataFrame) -> pd.Series:
    """
    Calculate On-Balance Volume (OBV).

    OBV uses volume flow to predict changes in stock price.

    Formula:
        - If Close > Close(previous): OBV = OBV(previous) + Volume
        - If Close < Close(previous): OBV = OBV(previous) - Volume
        - If Close = Close(previous): OBV = OBV(previous)

    Interpretation:
        - OBV rising with price: Confirms uptrend
        - OBV falling with price: Confirms downtrend
        - OBV diverging from price: Potential reversal

    Args:
        df: DataFrame with columns: Close, Volume

    Returns:
        pd.Series: OBV values
    """
    obv = pd.Series(index=df.index, dtype='float64')
    obv.iloc[0] = df['Volume'].iloc[0]

    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['Close'].iloc[i - 1]:
            obv.iloc[i] = obv.iloc[i - 1] + df['Volume'].iloc[i]
        elif df['Close'].iloc[i] < df['Close'].iloc[i - 1]:
            obv.iloc[i] = obv.iloc[i - 1] - df['Volume'].iloc[i]
        else:
            obv.iloc[i] = obv.iloc[i - 1]

    return obv


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all technical indicators to a DataFrame.

    This is a convenience function that calculates and adds all indicators
    as new columns to the input DataFrame.

    Args:
        df: DataFrame with OHLCV data (Open, High, Low, Close, Volume)

    Returns:
        pd.DataFrame: Original DataFrame with added indicator columns
    """
    result_df = df.copy()

    # Moving Averages
    result_df['SMA_20'] = calculate_sma(df['Close'], 20)
    result_df['SMA_50'] = calculate_sma(df['Close'], 50)
    result_df['SMA_200'] = calculate_sma(df['Close'], 200)
    result_df['EMA_12'] = calculate_ema(df['Close'], 12)
    result_df['EMA_26'] = calculate_ema(df['Close'], 26)

    # RSI
    result_df['RSI'] = calculate_rsi(df['Close'])

    # MACD
    macd, signal, histogram = calculate_macd(df['Close'])
    result_df['MACD'] = macd
    result_df['MACD_Signal'] = signal
    result_df['MACD_Histogram'] = histogram

    # Bollinger Bands
    bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(df['Close'])
    result_df['BB_Upper'] = bb_upper
    result_df['BB_Middle'] = bb_middle
    result_df['BB_Lower'] = bb_lower

    # VWAP (if Volume data exists)
    if 'Volume' in df.columns:
        result_df['VWAP'] = calculate_vwap(df)
        result_df['OBV'] = calculate_obv(df)

    return result_df


def identify_crossover(series1: pd.Series, series2: pd.Series) -> pd.Series:
    """
    Identify crossover points between two series.

    Args:
        series1: First series (e.g., fast MA)
        series2: Second series (e.g., slow MA)

    Returns:
        pd.Series: 1 for bullish crossover (series1 crosses above series2),
                  -1 for bearish crossover (series1 crosses below series2),
                  0 for no crossover
    """
    crossover = pd.Series(0, index=series1.index)

    # Bullish crossover: series1 was below, now above
    bullish = (series1 > series2) & (series1.shift(1) <= series2.shift(1))
    crossover[bullish] = 1

    # Bearish crossover: series1 was above, now below
    bearish = (series1 < series2) & (series1.shift(1) >= series2.shift(1))
    crossover[bearish] = -1

    return crossover


def identify_golden_death_cross(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify Golden Cross and Death Cross patterns.

    Golden Cross: 50-day SMA crosses above 200-day SMA (bullish)
    Death Cross: 50-day SMA crosses below 200-day SMA (bearish)

    Args:
        df: DataFrame with Close prices

    Returns:
        pd.DataFrame: DataFrame with 'Golden_Cross' and 'Death_Cross' columns
    """
    result_df = df.copy()

    sma_50 = calculate_sma(df['Close'], 50)
    sma_200 = calculate_sma(df['Close'], 200)

    crossover = identify_crossover(sma_50, sma_200)

    result_df['Golden_Cross'] = (crossover == 1)
    result_df['Death_Cross'] = (crossover == -1)

    return result_df
