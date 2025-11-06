"""
Data fetcher module for retrieving financial data using yfinance.

This module provides functions to:
- Fetch historical price data for single or multiple tickers
- Retrieve fundamental company information
- Download financial statements
"""

import pandas as pd
import yfinance as yf
from typing import Optional, Union, List, Dict
import warnings

# Suppress yfinance warnings
warnings.filterwarnings('ignore')


def validate_ticker(ticker: Optional[str]) -> bool:
    """
    Validate if a ticker symbol is valid by attempting to fetch its info.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'SPY')

    Returns:
        bool: True if ticker is valid, False otherwise
    """
    if not ticker or not isinstance(ticker, str):
        return False

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Check if we got meaningful data back
        if not info or 'symbol' not in info:
            return False

        return True
    except Exception:
        return False


def fetch_historical_data(
    ticker: str,
    period: Optional[str] = '1mo',
    interval: Optional[str] = '1d',
    start: Optional[str] = None,
    end: Optional[str] = None
) -> pd.DataFrame:
    """
    Fetch historical OHLCV data for a given ticker.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'SPY')
        period: Data period to download (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        start: Start date string (YYYY-MM-DD)
        end: End date string (YYYY-MM-DD)

    Returns:
        pd.DataFrame: DataFrame with OHLCV data and DatetimeIndex

    Raises:
        ValueError: If ticker is invalid or data cannot be fetched
    """
    if not validate_ticker(ticker):
        raise ValueError(f"Invalid ticker: {ticker}")

    try:
        stock = yf.Ticker(ticker)

        # Fetch data using period or start/end dates
        if start and end:
            df = stock.history(start=start, end=end, interval=interval)
        else:
            df = stock.history(period=period, interval=interval)

        if df.empty:
            raise ValueError(f"No data returned for ticker: {ticker}")

        # Clean up the DataFrame
        df.index.name = 'Date'

        return df

    except Exception as e:
        if "Invalid ticker" in str(e):
            raise
        raise ValueError(f"Error fetching data for {ticker}: {str(e)}")


def fetch_multiple_tickers(
    tickers: List[str],
    period: Optional[str] = '1mo',
    interval: Optional[str] = '1d',
    start: Optional[str] = None,
    end: Optional[str] = None
) -> Dict[str, pd.DataFrame]:
    """
    Fetch historical data for multiple tickers.

    Args:
        tickers: List of ticker symbols
        period: Data period to download
        interval: Data interval
        start: Start date string (YYYY-MM-DD)
        end: End date string (YYYY-MM-DD)

    Returns:
        dict: Dictionary mapping ticker symbols to their DataFrames
    """
    if not tickers:
        return {}

    results = {}

    for ticker in tickers:
        try:
            df = fetch_historical_data(
                ticker=ticker,
                period=period,
                interval=interval,
                start=start,
                end=end
            )
            results[ticker] = df
        except ValueError as e:
            # Skip invalid tickers, log warning
            print(f"Warning: Skipping {ticker} - {str(e)}")
            continue
        except Exception as e:
            print(f"Warning: Error fetching {ticker} - {str(e)}")
            continue

    return results


def fetch_ticker_info(ticker: str) -> Dict:
    """
    Fetch fundamental information for a given ticker.

    Args:
        ticker: Stock ticker symbol

    Returns:
        dict: Dictionary containing company information

    Raises:
        ValueError: If ticker is invalid
    """
    if not validate_ticker(ticker):
        raise ValueError(f"Invalid ticker: {ticker}")

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info:
            raise ValueError(f"No information available for ticker: {ticker}")

        # Return the full info dictionary
        return info

    except Exception as e:
        if "Invalid ticker" in str(e):
            raise
        raise ValueError(f"Error fetching info for {ticker}: {str(e)}")


def fetch_financial_statements(ticker: str) -> Dict[str, pd.DataFrame]:
    """
    Fetch financial statements (Income Statement, Balance Sheet, Cash Flow) for a ticker.

    Args:
        ticker: Stock ticker symbol

    Returns:
        dict: Dictionary containing three DataFrames:
            - 'income_statement': Income statement data
            - 'balance_sheet': Balance sheet data
            - 'cash_flow': Cash flow statement data

    Raises:
        ValueError: If ticker is invalid or statements cannot be fetched
    """
    if not validate_ticker(ticker):
        raise ValueError(f"Invalid ticker: {ticker}")

    try:
        stock = yf.Ticker(ticker)

        # Fetch financial statements
        income_stmt = stock.financials
        balance_sheet = stock.balance_sheet
        cash_flow = stock.cashflow

        # Check if we got valid data
        if income_stmt is None or balance_sheet is None or cash_flow is None:
            raise ValueError(f"No financial statements available for ticker: {ticker}")

        statements = {
            'income_statement': income_stmt,
            'balance_sheet': balance_sheet,
            'cash_flow': cash_flow
        }

        return statements

    except Exception as e:
        if "Invalid ticker" in str(e):
            raise
        raise ValueError(f"Error fetching financial statements for {ticker}: {str(e)}")
