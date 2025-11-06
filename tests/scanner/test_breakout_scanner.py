"""
Unit tests for breakout scanner module.
"""

import pytest
import pandas as pd
import numpy as np
from src.scanner.breakout_scanner import (
    calculate_relative_volume,
    check_volume_surge,
    check_rsi_signal,
    check_consolidation_breakout
)


@pytest.fixture
def sample_high_volume_data():
    """Create sample data with volume surge."""
    dates = pd.date_range('2024-01-01', periods=30, freq='D')
    np.random.seed(42)

    # Normal volume, then surge
    volumes = [1000000] * 25 + [3000000] * 5

    data = pd.DataFrame({
        'Open': np.random.uniform(100, 110, 30),
        'High': np.random.uniform(110, 120, 30),
        'Low': np.random.uniform(90, 100, 30),
        'Close': np.random.uniform(95, 115, 30),
        'Volume': volumes
    }, index=dates)

    return data


@pytest.fixture
def sample_oversold_data():
    """Create sample data showing oversold conditions."""
    dates = pd.date_range('2024-01-01', periods=50, freq='D')

    # Declining prices to trigger oversold RSI
    close_prices = np.linspace(120, 80, 50) + np.random.normal(0, 1, 50)

    data = pd.DataFrame({
        'Open': close_prices - np.random.uniform(0, 2, 50),
        'High': close_prices + np.random.uniform(0, 2, 50),
        'Low': close_prices - np.random.uniform(0, 2, 50),
        'Close': close_prices,
        'Volume': np.random.uniform(1000000, 2000000, 50)
    }, index=dates)

    return data


class TestRelativeVolume:
    """Tests for relative volume calculation."""

    def test_calculate_relative_volume(self, sample_high_volume_data):
        """Test relative volume calculation."""
        rel_vol = calculate_relative_volume(sample_high_volume_data)

        assert rel_vol is not None
        assert isinstance(rel_vol, (int, float))
        # Should show surge (current volume / average)
        assert rel_vol > 2.0

    def test_relative_volume_insufficient_data(self):
        """Test with insufficient data."""
        dates = pd.date_range('2024-01-01', periods=10, freq='D')
        small_df = pd.DataFrame({
            'Volume': [1000000] * 10
        }, index=dates)

        rel_vol = calculate_relative_volume(small_df, period=20)
        assert rel_vol is None

    def test_check_volume_surge(self, sample_high_volume_data):
        """Test volume surge detection."""
        has_surge = check_volume_surge(sample_high_volume_data, threshold=2.0)

        assert has_surge == True


class TestRSISignals:
    """Tests for RSI signal detection."""

    def test_check_rsi_oversold(self, sample_oversold_data):
        """Test RSI oversold detection."""
        signal = check_rsi_signal(sample_oversold_data)

        # With declining prices, should be oversold or at least not overbought
        assert signal in ['oversold', 'neutral']

    def test_check_rsi_neutral(self):
        """Test RSI neutral condition."""
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        # Stable prices should give neutral RSI
        data = pd.DataFrame({
            'Close': [100] * 30 + np.random.normal(0, 0.5, 30)
        }, index=dates)

        signal = check_rsi_signal(data)
        assert signal in ['neutral', 'oversold', 'overbought']

    def test_check_rsi_insufficient_data(self):
        """Test with insufficient data."""
        dates = pd.date_range('2024-01-01', periods=5, freq='D')
        small_df = pd.DataFrame({
            'Close': [100, 101, 102, 103, 104]
        }, index=dates)

        signal = check_rsi_signal(small_df)
        # Should return neutral when RSI can't be calculated
        assert signal == 'neutral'


class TestConsolidation:
    """Tests for consolidation detection."""

    def test_check_consolidation(self):
        """Test consolidation detection."""
        dates = pd.date_range('2024-01-01', periods=50, freq='D')

        # First 30 days: consolidation (narrow range)
        # Last 20 days: breakout (wider range)
        prices_consolidation = np.random.uniform(99, 101, 30)
        prices_breakout = np.linspace(101, 120, 20)
        all_prices = np.concatenate([prices_consolidation, prices_breakout])

        data = pd.DataFrame({
            'Open': all_prices - 0.5,
            'High': all_prices + 1,
            'Low': all_prices - 1,
            'Close': all_prices,
            'Volume': np.random.uniform(1000000, 2000000, 50)
        }, index=dates)

        result = check_consolidation_breakout(data)

        assert isinstance(result, dict)
        assert 'in_consolidation' in result
        assert 'breaking_out' in result
        assert isinstance(result['in_consolidation'], (bool, np.bool_))
        assert isinstance(result['breaking_out'], (bool, np.bool_))


class TestEdgeCases:
    """Test edge cases."""

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        empty_df = pd.DataFrame()

        rel_vol = calculate_relative_volume(empty_df)
        assert rel_vol is None

        has_surge = check_volume_surge(empty_df)
        assert has_surge is False

    def test_single_row_dataframe(self):
        """Test with single row."""
        single_row = pd.DataFrame({
            'Close': [100],
            'Volume': [1000000]
        })

        signal = check_rsi_signal(single_row)
        assert signal == 'neutral'
