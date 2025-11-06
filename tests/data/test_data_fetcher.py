"""
Unit tests for data_fetcher module.
Following TDD approach - these tests will fail until implementation is complete.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from src.data.data_fetcher import (
    fetch_historical_data,
    fetch_multiple_tickers,
    fetch_ticker_info,
    fetch_financial_statements,
    validate_ticker
)


class TestFetchHistoricalData:
    """Test suite for fetch_historical_data function."""

    def test_fetch_valid_ticker(self):
        """Test fetching data for a valid ticker."""
        df = fetch_historical_data('AAPL', period='1mo', interval='1d')

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert all(col in df.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume'])
        assert isinstance(df.index, pd.DatetimeIndex)

    def test_fetch_invalid_ticker(self):
        """Test that invalid ticker raises appropriate error."""
        with pytest.raises(ValueError, match="Invalid ticker"):
            fetch_historical_data('INVALID_TICKER_XYZ', period='1mo', interval='1d')

    def test_fetch_with_custom_date_range(self):
        """Test fetching data with specific start and end dates."""
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')

        df = fetch_historical_data('SPY', start=start_date, end=end_date, interval='1d')

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert df.index[0].date() >= datetime.strptime(start_date, '%Y-%m-%d').date()

    def test_fetch_different_intervals(self):
        """Test fetching data with different time intervals."""
        df_daily = fetch_historical_data('MSFT', period='5d', interval='1d')
        df_hourly = fetch_historical_data('MSFT', period='5d', interval='1h')

        assert len(df_hourly) > len(df_daily)

    def test_dataframe_has_correct_dtypes(self):
        """Test that returned DataFrame has correct data types."""
        df = fetch_historical_data('GOOGL', period='1mo', interval='1d')

        assert df['Open'].dtype in ['float64', 'float32']
        assert df['Volume'].dtype in ['int64', 'int32', 'float64']


class TestFetchMultipleTickers:
    """Test suite for fetch_multiple_tickers function."""

    def test_fetch_multiple_valid_tickers(self):
        """Test fetching data for multiple valid tickers."""
        tickers = ['AAPL', 'MSFT', 'GOOGL']
        data_dict = fetch_multiple_tickers(tickers, period='1mo', interval='1d')

        assert isinstance(data_dict, dict)
        assert len(data_dict) == 3
        assert all(ticker in data_dict for ticker in tickers)
        assert all(isinstance(df, pd.DataFrame) for df in data_dict.values())

    def test_fetch_mixed_valid_invalid_tickers(self):
        """Test that valid tickers are fetched even if some are invalid."""
        tickers = ['AAPL', 'INVALID_XYZ', 'MSFT']
        data_dict = fetch_multiple_tickers(tickers, period='1mo', interval='1d')

        # Should successfully fetch valid tickers
        assert 'AAPL' in data_dict
        assert 'MSFT' in data_dict
        # Invalid ticker should be skipped
        assert 'INVALID_XYZ' not in data_dict

    def test_empty_ticker_list(self):
        """Test that empty ticker list returns empty dict."""
        data_dict = fetch_multiple_tickers([], period='1mo', interval='1d')
        assert data_dict == {}


class TestFetchTickerInfo:
    """Test suite for fetch_ticker_info function."""

    def test_fetch_valid_ticker_info(self):
        """Test fetching info for a valid ticker."""
        info = fetch_ticker_info('AAPL')

        assert isinstance(info, dict)
        assert 'longName' in info or 'shortName' in info
        assert 'sector' in info
        assert 'industry' in info
        assert 'marketCap' in info

    def test_fetch_invalid_ticker_info(self):
        """Test that invalid ticker raises error."""
        with pytest.raises(ValueError, match="Invalid ticker"):
            fetch_ticker_info('INVALID_TICKER_XYZ')

    def test_ticker_info_has_expected_fields(self):
        """Test that ticker info contains expected fundamental fields."""
        info = fetch_ticker_info('MSFT')

        expected_fields = ['sector', 'industry', 'marketCap']
        for field in expected_fields:
            assert field in info


class TestFetchFinancialStatements:
    """Test suite for fetch_financial_statements function."""

    def test_fetch_financial_statements(self):
        """Test fetching all three financial statements."""
        statements = fetch_financial_statements('AAPL')

        assert isinstance(statements, dict)
        assert 'income_statement' in statements
        assert 'balance_sheet' in statements
        assert 'cash_flow' in statements

        # Each should be a DataFrame
        assert isinstance(statements['income_statement'], pd.DataFrame)
        assert isinstance(statements['balance_sheet'], pd.DataFrame)
        assert isinstance(statements['cash_flow'], pd.DataFrame)

    def test_financial_statements_not_empty(self):
        """Test that financial statements contain data."""
        statements = fetch_financial_statements('MSFT')

        assert not statements['income_statement'].empty
        assert not statements['balance_sheet'].empty
        assert not statements['cash_flow'].empty

    def test_invalid_ticker_financial_statements(self):
        """Test that invalid ticker raises error."""
        with pytest.raises(ValueError, match="Invalid ticker"):
            fetch_financial_statements('INVALID_TICKER_XYZ')


class TestValidateTicker:
    """Test suite for validate_ticker helper function."""

    def test_validate_valid_ticker(self):
        """Test that valid ticker returns True."""
        assert validate_ticker('AAPL') is True
        assert validate_ticker('SPY') is True

    def test_validate_invalid_ticker(self):
        """Test that invalid ticker returns False."""
        assert validate_ticker('INVALID_XYZ') is False
        assert validate_ticker('') is False

    def test_validate_none_ticker(self):
        """Test that None ticker returns False."""
        assert validate_ticker(None) is False
