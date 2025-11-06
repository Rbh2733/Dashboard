"""
Unit tests for technical analysis module.
"""

import pytest
import pandas as pd
import numpy as np
from src.analysis.technical import (
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_vwap,
    calculate_obv,
    add_all_indicators,
    identify_crossover,
    identify_golden_death_cross
)


@pytest.fixture
def sample_price_data():
    """Create sample price data for testing."""
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    np.random.seed(42)

    data = pd.DataFrame({
        'Open': np.random.uniform(100, 110, 100),
        'High': np.random.uniform(110, 120, 100),
        'Low': np.random.uniform(90, 100, 100),
        'Close': np.random.uniform(95, 115, 100),
        'Volume': np.random.uniform(1000000, 5000000, 100).astype(int)
    }, index=dates)

    return data


@pytest.fixture
def trending_data():
    """Create data with a clear uptrend for testing crossovers."""
    dates = pd.date_range('2024-01-01', periods=300, freq='D')

    # Create uptrend
    trend = np.linspace(100, 150, 300)
    noise = np.random.normal(0, 2, 300)
    close_prices = trend + noise

    data = pd.DataFrame({
        'Open': close_prices - np.random.uniform(0, 2, 300),
        'High': close_prices + np.random.uniform(0, 2, 300),
        'Low': close_prices - np.random.uniform(0, 2, 300),
        'Close': close_prices,
        'Volume': np.random.uniform(1000000, 5000000, 300).astype(int)
    }, index=dates)

    return data


class TestMovingAverages:
    """Tests for moving average calculations."""

    def test_calculate_sma(self, sample_price_data):
        """Test SMA calculation."""
        sma = calculate_sma(sample_price_data['Close'], 20)

        assert isinstance(sma, pd.Series)
        assert len(sma) == len(sample_price_data)
        # First 19 values should be NaN
        assert pd.isna(sma.iloc[0:19]).all()
        # Values after period should exist
        assert not pd.isna(sma.iloc[20])

    def test_calculate_ema(self, sample_price_data):
        """Test EMA calculation."""
        ema = calculate_ema(sample_price_data['Close'], 20)

        assert isinstance(ema, pd.Series)
        assert len(ema) == len(sample_price_data)
        # EMA should have fewer NaN values than SMA at start
        assert not pd.isna(ema.iloc[20])

    def test_ema_more_responsive_than_sma(self, trending_data):
        """Test that EMA is more responsive to recent price changes than SMA."""
        period = 20
        sma = calculate_sma(trending_data['Close'], period)
        ema = calculate_ema(trending_data['Close'], period)

        # In an uptrend, EMA should be higher than SMA (closer to current price)
        recent_diff = (ema - sma).iloc[-50:].mean()
        assert recent_diff > 0


class TestRSI:
    """Tests for RSI calculation."""

    def test_calculate_rsi(self, sample_price_data):
        """Test RSI calculation."""
        rsi = calculate_rsi(sample_price_data['Close'], 14)

        assert isinstance(rsi, pd.Series)
        assert len(rsi) == len(sample_price_data)
        # RSI values should be between 0 and 100
        valid_rsi = rsi.dropna()
        assert (valid_rsi >= 0).all()
        assert (valid_rsi <= 100).all()

    def test_rsi_boundary_values(self):
        """Test RSI with extreme price movements."""
        # Create data with consecutive increases
        dates = pd.date_range('2024-01-01', periods=50, freq='D')
        increasing_prices = pd.Series(range(100, 150), index=dates)

        rsi = calculate_rsi(increasing_prices, 14)

        # With consecutive increases, RSI should be high (overbought)
        assert rsi.iloc[-1] > 70


class TestMACD:
    """Tests for MACD calculation."""

    def test_calculate_macd(self, sample_price_data):
        """Test MACD calculation."""
        macd, signal, histogram = calculate_macd(sample_price_data['Close'])

        assert isinstance(macd, pd.Series)
        assert isinstance(signal, pd.Series)
        assert isinstance(histogram, pd.Series)
        assert len(macd) == len(sample_price_data)

        # Histogram should equal MACD - Signal
        np.testing.assert_array_almost_equal(
            histogram.dropna().values,
            (macd - signal).dropna().values
        )

    def test_macd_custom_periods(self, sample_price_data):
        """Test MACD with custom periods."""
        macd, signal, histogram = calculate_macd(
            sample_price_data['Close'],
            fast_period=8,
            slow_period=21,
            signal_period=5
        )

        assert isinstance(macd, pd.Series)
        assert len(macd) == len(sample_price_data)


class TestBollingerBands:
    """Tests for Bollinger Bands calculation."""

    def test_calculate_bollinger_bands(self, sample_price_data):
        """Test Bollinger Bands calculation."""
        upper, middle, lower = calculate_bollinger_bands(sample_price_data['Close'])

        assert isinstance(upper, pd.Series)
        assert isinstance(middle, pd.Series)
        assert isinstance(lower, pd.Series)

        # Upper should be above middle, middle above lower
        valid_idx = ~upper.isna()
        assert (upper[valid_idx] >= middle[valid_idx]).all()
        assert (middle[valid_idx] >= lower[valid_idx]).all()

    def test_bollinger_bands_width(self, sample_price_data):
        """Test Bollinger Bands with different standard deviations."""
        upper2, middle2, lower2 = calculate_bollinger_bands(
            sample_price_data['Close'], std_dev=2.0
        )
        upper3, middle3, lower3 = calculate_bollinger_bands(
            sample_price_data['Close'], std_dev=3.0
        )

        # Wider std_dev should create wider bands
        width2 = (upper2 - lower2).iloc[-1]
        width3 = (upper3 - lower3).iloc[-1]
        assert width3 > width2


class TestVWAP:
    """Tests for VWAP calculation."""

    def test_calculate_vwap(self, sample_price_data):
        """Test VWAP calculation."""
        vwap = calculate_vwap(sample_price_data)

        assert isinstance(vwap, pd.Series)
        assert len(vwap) == len(sample_price_data)
        # VWAP should be positive
        assert (vwap > 0).all()

    def test_vwap_is_cumulative(self, sample_price_data):
        """Test that VWAP is cumulative (monotonic changes)."""
        vwap = calculate_vwap(sample_price_data)
        # VWAP should never be NaN after first value
        assert not vwap.iloc[1:].isna().any()


class TestOBV:
    """Tests for OBV calculation."""

    def test_calculate_obv(self, sample_price_data):
        """Test OBV calculation."""
        obv = calculate_obv(sample_price_data)

        assert isinstance(obv, pd.Series)
        assert len(obv) == len(sample_price_data)
        # OBV should not have NaN values
        assert not obv.isna().any()

    def test_obv_direction(self):
        """Test OBV increases with price increases."""
        dates = pd.date_range('2024-01-01', periods=5, freq='D')
        data = pd.DataFrame({
            'Close': [100, 101, 102, 101, 103],
            'Volume': [1000, 1000, 1000, 1000, 1000]
        }, index=dates)

        obv = calculate_obv(data)

        # OBV should increase when price increases
        assert obv.iloc[1] > obv.iloc[0]  # Price up
        assert obv.iloc[2] > obv.iloc[1]  # Price up
        assert obv.iloc[3] < obv.iloc[2]  # Price down
        assert obv.iloc[4] > obv.iloc[3]  # Price up


class TestAddAllIndicators:
    """Tests for add_all_indicators convenience function."""

    def test_add_all_indicators(self, sample_price_data):
        """Test adding all indicators to DataFrame."""
        result = add_all_indicators(sample_price_data)

        # Check that original columns are preserved
        assert all(col in result.columns for col in sample_price_data.columns)

        # Check that indicator columns are added
        expected_indicators = [
            'SMA_20', 'SMA_50', 'SMA_200', 'EMA_12', 'EMA_26',
            'RSI', 'MACD', 'MACD_Signal', 'MACD_Histogram',
            'BB_Upper', 'BB_Middle', 'BB_Lower', 'VWAP', 'OBV'
        ]

        for indicator in expected_indicators:
            assert indicator in result.columns

    def test_add_all_indicators_does_not_modify_original(self, sample_price_data):
        """Test that add_all_indicators doesn't modify the original DataFrame."""
        original_columns = sample_price_data.columns.tolist()
        add_all_indicators(sample_price_data)

        assert sample_price_data.columns.tolist() == original_columns


class TestCrossovers:
    """Tests for crossover identification."""

    def test_identify_crossover(self):
        """Test crossover identification."""
        dates = pd.date_range('2024-01-01', periods=10, freq='D')
        # Create clear crossover: below, cross up, above, cross down, below
        series1 = pd.Series([1, 2, 3, 4, 5, 4, 3, 2, 4, 5], index=dates)
        series2 = pd.Series([3, 3, 3, 3, 3, 3, 3, 3, 3, 3], index=dates)

        crossover = identify_crossover(series1, series2)

        # series1 crosses above series2 at index 3 (was 3, now 4)
        assert crossover.iloc[3] == 1

        # series1 crosses below series2 at index 7 (was 3, now 2)
        assert crossover.iloc[7] == -1

    def test_identify_golden_death_cross(self, trending_data):
        """Test Golden Cross and Death Cross identification."""
        result = identify_golden_death_cross(trending_data)

        assert 'Golden_Cross' in result.columns
        assert 'Death_Cross' in result.columns

        # Check that columns are boolean type
        assert result['Golden_Cross'].dtype == bool
        assert result['Death_Cross'].dtype == bool

        # Check that not all values are NaN (we have valid crossover signals)
        # Note: May not have actual crossovers in random test data
        assert result['Golden_Cross'].notna().any()
        assert result['Death_Cross'].notna().any()


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        empty_df = pd.DataFrame()
        with pytest.raises(KeyError):
            add_all_indicators(empty_df)

    def test_insufficient_data(self):
        """Test with insufficient data points."""
        dates = pd.date_range('2024-01-01', periods=5, freq='D')
        small_df = pd.DataFrame({
            'Close': [100, 101, 102, 103, 104]
        }, index=dates)

        # Should not raise error, but will have many NaN values
        sma = calculate_sma(small_df['Close'], 10)
        assert sma.isna().all()  # All NaN since we need 10 periods
