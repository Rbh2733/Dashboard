"""
Market Scanner Page

Scan multiple stocks for:
- Breakout opportunities
- High volume movers
- RSI extremes
- Golden/Death crosses
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.scanner.breakout_scanner import (
    scan_multiple_tickers,
    find_high_volume_movers,
    find_oversold_stocks,
    find_golden_cross_stocks,
    find_breakout_candidates,
    SP500_SAMPLE,
    ETF_LIST
)

st.set_page_config(page_title="Market Scanner", page_icon="🔍", layout="wide")

st.title("🔍 Market Scanner")
st.markdown("Scan the market for breakout opportunities and trading signals")

# Sidebar
with st.sidebar:
    st.header("Scanner Settings")

    scan_type = st.selectbox(
        "Scan Type",
        options=[
            "Breakout Candidates",
            "High Volume Movers",
            "Oversold Stocks (RSI)",
            "Golden Cross",
            "Custom Scan"
        ]
    )

    ticker_list = st.radio(
        "Ticker List",
        options=["S&P 500 Sample", "ETFs", "Custom"],
        index=0
    )

    if ticker_list == "Custom":
        custom_tickers = st.text_area(
            "Enter Tickers (comma separated)",
            value="AAPL,MSFT,GOOGL,AMZN,TSLA",
            height=100
        )
        tickers = [t.strip().upper() for t in custom_tickers.split(',') if t.strip()]
    elif ticker_list == "ETFs":
        tickers = ETF_LIST
    else:
        tickers = SP500_SAMPLE

    st.info(f"📊 Scanning {len(tickers)} tickers")

    # Custom filters for Custom Scan
    if scan_type == "Custom Scan":
        st.markdown("---")
        st.subheader("Filters")
        min_rel_volume = st.slider("Min Relative Volume", 1.0, 5.0, 1.5, 0.5)
        near_52w = st.checkbox("Near 52-Week High", value=False)
        volume_surge = st.checkbox("Volume Surge Only", value=False)

    scan_button = st.button("🔍 Run Scan", type="primary", use_container_width=True)

# Main content
if scan_button:
    with st.spinner(f"Scanning {len(tickers)} tickers... This may take a minute..."):
        try:
            if scan_type == "Breakout Candidates":
                results = find_breakout_candidates(tickers)
                st.success(f"✅ Found {len(results)} breakout candidates")

            elif scan_type == "High Volume Movers":
                results = find_high_volume_movers(tickers, min_rel_volume=2.0)
                st.success(f"✅ Found {len(results)} high volume movers")

            elif scan_type == "Oversold Stocks (RSI)":
                results = find_oversold_stocks(tickers)
                st.success(f"✅ Found {len(results)} oversold stocks")

            elif scan_type == "Golden Cross":
                results = find_golden_cross_stocks(tickers)
                st.success(f"✅ Found {len(results)} stocks with golden cross")

            elif scan_type == "Custom Scan":
                results = scan_multiple_tickers(tickers)

                # Apply custom filters
                if not results.empty:
                    if volume_surge:
                        results = results[results['volume_surge'] == True]
                    if near_52w:
                        results = results[results['near_52w_high'] == True]
                    if 'relative_volume' in results.columns:
                        results = results[results['relative_volume'] >= min_rel_volume]

                st.success(f"✅ Found {len(results)} stocks matching filters")

            if results.empty:
                st.warning("No results found matching the criteria.")
                st.info("Try adjusting the filters or selecting a different ticker list.")
            else:
                # Display results
                st.markdown("---")
                st.subheader("Scan Results")

                # Prepare display dataframe
                display_df = results.copy()

                # Format columns
                if 'current_price' in display_df.columns:
                    display_df['current_price'] = display_df['current_price'].round(2)

                if 'relative_volume' in display_df.columns:
                    display_df['relative_volume'] = display_df['relative_volume'].round(2)

                if 'rsi_value' in display_df.columns:
                    display_df['rsi_value'] = display_df['rsi_value'].round(2)

                if 'price_change_5d' in display_df.columns:
                    display_df['price_change_5d'] = display_df['price_change_5d'].round(2)

                if 'price_change_20d' in display_df.columns:
                    display_df['price_change_20d'] = display_df['price_change_20d'].round(2)

                # Select relevant columns for display
                display_columns = ['ticker', 'current_price']

                if 'relative_volume' in display_df.columns:
                    display_columns.append('relative_volume')

                if 'rsi_value' in display_df.columns:
                    display_columns.append('rsi_value')

                if 'rsi_signal' in display_df.columns:
                    display_columns.append('rsi_signal')

                if 'price_change_5d' in display_df.columns:
                    display_columns.append('price_change_5d')

                if 'price_change_20d' in display_df.columns:
                    display_columns.append('price_change_20d')

                if 'volume_surge' in display_df.columns:
                    display_columns.append('volume_surge')

                if 'near_52w_high' in display_df.columns:
                    display_columns.append('near_52w_high')

                if 'ma_crossover' in display_df.columns:
                    display_columns.append('ma_crossover')

                if 'breakout_score' in display_df.columns:
                    display_columns.append('breakout_score')

                # Filter to existing columns
                display_columns = [col for col in display_columns if col in display_df.columns]

                # Show dataframe
                st.dataframe(
                    display_df[display_columns],
                    use_container_width=True,
                    height=400
                )

                # Download button
                csv = display_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name=f"{scan_type.lower().replace(' ', '_')}_results.csv",
                    mime="text/csv"
                )

                # Top picks
                if len(results) > 0:
                    st.markdown("---")
                    st.subheader("📌 Top Picks")

                    # Show top 5
                    top_picks = display_df.head(5)

                    for idx, row in top_picks.iterrows():
                        with st.expander(f"**{row['ticker']}** - ${row.get('current_price', 'N/A')}"):
                            col1, col2, col3 = st.columns(3)

                            with col1:
                                if 'relative_volume' in row:
                                    st.metric("Relative Volume", f"{row['relative_volume']:.2f}x")
                                if 'volume_surge' in row:
                                    surge_emoji = "🚀" if row['volume_surge'] else ""
                                    st.write(f"Volume Surge: {row['volume_surge']} {surge_emoji}")

                            with col2:
                                if 'rsi_value' in row:
                                    st.metric("RSI", f"{row['rsi_value']:.2f}")
                                if 'rsi_signal' in row:
                                    signal = row['rsi_signal']
                                    if signal == 'oversold':
                                        st.success("✅ Oversold")
                                    elif signal == 'overbought':
                                        st.warning("⚠️ Overbought")

                            with col3:
                                if 'price_change_5d' in row and pd.notna(row['price_change_5d']):
                                    st.metric("5D Change", f"{row['price_change_5d']:+.2f}%")
                                if 'near_52w_high' in row:
                                    if row['near_52w_high']:
                                        st.info("📈 Near 52W High")

        except Exception as e:
            st.error(f"Error running scan: {str(e)}")
            st.exception(e)

else:
    # Initial state
    st.info("👆 Configure your scan settings in the sidebar and click 'Run Scan' to get started.")

    st.markdown("---")
    st.subheader("Available Scan Types")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Breakout Candidates** 🚀
        - Breaking out of consolidation
        - Near 52-week high with volume
        - Golden cross with high volume
        - Composite breakout score

        **High Volume Movers** 📊
        - Relative volume > 2x average
        - Sorted by volume activity
        - Potential momentum plays
        """)

    with col2:
        st.markdown("""
        **Oversold Stocks (RSI)** 📉
        - RSI < 30
        - Potential reversal plays
        - Sorted by RSI value

        **Golden Cross** ⭐
        - 50-day SMA crossed above 200-day SMA
        - Bullish long-term signal
        - Requires at least 1 year of data
        """)

    st.markdown("""
    **Custom Scan** 🎯
    - Define your own criteria
    - Combine multiple filters
    - Flexible screening
    """)
