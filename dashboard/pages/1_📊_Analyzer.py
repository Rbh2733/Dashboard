"""
Stock/ETF Analyzer Page

Analyze individual stocks and ETFs with:
- Interactive price charts
- Technical indicators
- Fundamental metrics
- Pattern recognition
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data.data_fetcher import fetch_historical_data, fetch_ticker_info
from src.analysis.technical import add_all_indicators, calculate_rsi, calculate_macd
from src.analysis.fundamental import create_fundamental_summary
from src.analysis.patterns import add_all_patterns, summarize_patterns

st.set_page_config(page_title="Stock Analyzer", page_icon="📊", layout="wide")

st.title("📊 Stock/ETF Analyzer")
st.markdown("Analyze stocks and ETFs with technical indicators and fundamental data")

# Sidebar inputs
with st.sidebar:
    st.header("Settings")

    ticker = st.text_input("Enter Ticker Symbol", value="AAPL", max_chars=10).upper()

    period = st.selectbox(
        "Time Period",
        options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=3
    )

    show_indicators = st.multiselect(
        "Technical Indicators",
        options=["SMA 20", "SMA 50", "SMA 200", "Bollinger Bands", "VWAP"],
        default=["SMA 50", "SMA 200"]
    )

    show_volume = st.checkbox("Show Volume", value=True)
    show_rsi = st.checkbox("Show RSI", value=True)
    show_macd = st.checkbox("Show MACD", value=False)

    analyze_button = st.button("🔍 Analyze", type="primary", use_container_width=True)

# Main content
if analyze_button or ticker:
    try:
        with st.spinner(f"Fetching data for {ticker}..."):
            # Fetch data
            df = fetch_historical_data(ticker, period=period, interval='1d')

            if df.empty:
                st.error(f"No data found for ticker: {ticker}")
                st.stop()

            # Add indicators
            df = add_all_indicators(df)
            df = add_all_patterns(df)

            # Display current price
            current_price = df['Close'].iloc[-1]
            prev_close = df['Close'].iloc[-2] if len(df) > 1 else current_price
            price_change = current_price - prev_close
            price_change_pct = (price_change / prev_close) * 100

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Current Price",
                    f"${current_price:.2f}",
                    f"{price_change:+.2f} ({price_change_pct:+.2f}%)"
                )

            with col2:
                day_high = df['High'].iloc[-1]
                day_low = df['Low'].iloc[-1]
                st.metric("Day Range", f"${day_low:.2f} - ${day_high:.2f}")

            with col3:
                volume = df['Volume'].iloc[-1]
                st.metric("Volume", f"{volume:,.0f}")

            with col4:
                if 'RSI' in df.columns:
                    rsi_current = df['RSI'].iloc[-1]
                    if not pd.isna(rsi_current):
                        st.metric("RSI (14)", f"{rsi_current:.2f}")

            st.markdown("---")

            # Create main chart
            fig = make_subplots(
                rows=3 if (show_rsi or show_macd) else 2,
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=[0.6, 0.2, 0.2] if (show_rsi or show_macd) else [0.7, 0.3],
                subplot_titles=("Price", "Volume", "RSI/MACD" if (show_rsi or show_macd) else "")
            )

            # Price candlesticks
            fig.add_trace(
                go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name=ticker,
                    increasing_line_color='green',
                    decreasing_line_color='red'
                ),
                row=1, col=1
            )

            # Add selected indicators
            if "SMA 20" in show_indicators and 'SMA_20' in df.columns:
                fig.add_trace(
                    go.Scatter(x=df.index, y=df['SMA_20'], name="SMA 20",
                              line=dict(color='orange', width=1)),
                    row=1, col=1
                )

            if "SMA 50" in show_indicators and 'SMA_50' in df.columns:
                fig.add_trace(
                    go.Scatter(x=df.index, y=df['SMA_50'], name="SMA 50",
                              line=dict(color='blue', width=1.5)),
                    row=1, col=1
                )

            if "SMA 200" in show_indicators and 'SMA_200' in df.columns:
                fig.add_trace(
                    go.Scatter(x=df.index, y=df['SMA_200'], name="SMA 200",
                              line=dict(color='purple', width=2)),
                    row=1, col=1
                )

            if "Bollinger Bands" in show_indicators:
                if all(col in df.columns for col in ['BB_Upper', 'BB_Middle', 'BB_Lower']):
                    fig.add_trace(
                        go.Scatter(x=df.index, y=df['BB_Upper'], name="BB Upper",
                                  line=dict(color='gray', width=1, dash='dash')),
                        row=1, col=1
                    )
                    fig.add_trace(
                        go.Scatter(x=df.index, y=df['BB_Lower'], name="BB Lower",
                                  line=dict(color='gray', width=1, dash='dash'),
                                  fill='tonexty', fillcolor='rgba(128,128,128,0.1)'),
                        row=1, col=1
                    )

            if "VWAP" in show_indicators and 'VWAP' in df.columns:
                fig.add_trace(
                    go.Scatter(x=df.index, y=df['VWAP'], name="VWAP",
                              line=dict(color='brown', width=1.5)),
                    row=1, col=1
                )

            # Volume
            if show_volume:
                colors = ['green' if close >= open_ else 'red'
                         for close, open_ in zip(df['Close'], df['Open'])]

                fig.add_trace(
                    go.Bar(x=df.index, y=df['Volume'], name="Volume",
                          marker_color=colors, showlegend=False),
                    row=2, col=1
                )

            # RSI
            if show_rsi and 'RSI' in df.columns:
                fig.add_trace(
                    go.Scatter(x=df.index, y=df['RSI'], name="RSI",
                              line=dict(color='purple', width=2)),
                    row=3, col=1
                )
                # Add overbought/oversold lines
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

            # MACD
            if show_macd and 'MACD' in df.columns:
                fig.add_trace(
                    go.Scatter(x=df.index, y=df['MACD'], name="MACD",
                              line=dict(color='blue', width=1.5)),
                    row=3, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df.index, y=df['MACD_Signal'], name="Signal",
                              line=dict(color='orange', width=1.5)),
                    row=3, col=1
                )

            # Update layout
            fig.update_layout(
                height=800,
                showlegend=True,
                xaxis_rangeslider_visible=False,
                hovermode='x unified'
            )

            fig.update_yaxes(title_text="Price ($)", row=1, col=1)
            fig.update_yaxes(title_text="Volume", row=2, col=1)
            if show_rsi or show_macd:
                fig.update_yaxes(title_text="RSI/MACD", row=3, col=1)

            st.plotly_chart(fig, use_container_width=True)

            # Tabs for additional analysis
            tab1, tab2, tab3 = st.tabs(["📈 Technical Summary", "📊 Fundamentals", "🔍 Patterns"])

            with tab1:
                st.subheader("Technical Indicators Summary")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Moving Averages**")
                    if 'SMA_20' in df.columns:
                        st.write(f"SMA 20: ${df['SMA_20'].iloc[-1]:.2f}")
                    if 'SMA_50' in df.columns:
                        st.write(f"SMA 50: ${df['SMA_50'].iloc[-1]:.2f}")
                    if 'SMA_200' in df.columns:
                        st.write(f"SMA 200: ${df['SMA_200'].iloc[-1]:.2f}")

                with col2:
                    st.markdown("**Momentum Indicators**")
                    if 'RSI' in df.columns and not pd.isna(df['RSI'].iloc[-1]):
                        rsi = df['RSI'].iloc[-1]
                        st.write(f"RSI: {rsi:.2f}")
                        if rsi > 70:
                            st.warning("⚠️ Overbought")
                        elif rsi < 30:
                            st.success("✅ Oversold")

                    if 'MACD' in df.columns:
                        macd_val = df['MACD'].iloc[-1]
                        signal_val = df['MACD_Signal'].iloc[-1]
                        st.write(f"MACD: {macd_val:.2f}")
                        st.write(f"Signal: {signal_val:.2f}")

            with tab2:
                st.subheader("Fundamental Analysis")

                with st.spinner("Fetching fundamental data..."):
                    try:
                        info = fetch_ticker_info(ticker)
                        summary = create_fundamental_summary(info)

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.markdown("**Valuation**")
                            valuation = summary.get('Valuation', {})
                            for key, value in valuation.items():
                                if value is not None:
                                    st.write(f"{key.replace('_', ' ')}: {value:.2f}")

                        with col2:
                            st.markdown("**Profitability**")
                            profit = summary.get('Profitability', {})
                            for key, value in profit.items():
                                if value is not None:
                                    if 'Margin' in key:
                                        st.write(f"{key.replace('_', ' ')}: {value*100:.2f}%")
                                    else:
                                        st.write(f"{key.replace('_', ' ')}: {value:.2f}")

                        with col3:
                            st.markdown("**Growth**")
                            growth = summary.get('Growth', {})
                            for key, value in growth.items():
                                if value is not None and 'Growth' in key:
                                    st.write(f"{key.replace('_', ' ')}: {value*100:.2f}%")

                    except Exception as e:
                        st.error(f"Error fetching fundamental data: {str(e)}")

            with tab3:
                st.subheader("Pattern Recognition")

                pattern_summary = summarize_patterns(df)

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Candlestick Patterns (Last 30 Days)**")
                    st.write(f"Doji: {pattern_summary['doji_count']}")
                    st.write(f"Bullish Engulfing: {pattern_summary['bullish_engulfing_count']}")
                    st.write(f"Bearish Engulfing: {pattern_summary['bearish_engulfing_count']}")
                    st.write(f"Hammer: {pattern_summary['hammer_count']}")
                    st.write(f"Shooting Star: {pattern_summary['shooting_star_count']}")

                with col2:
                    st.markdown("**Chart Patterns**")
                    if pattern_summary['in_consolidation']:
                        st.info(f"📊 In Consolidation ({pattern_summary['consolidation_days']} days)")
                    else:
                        st.success("✅ Not in Consolidation")

                    st.markdown("**52-Week Stats**")
                    stats_52w = pattern_summary['52_week_stats']
                    st.write(f"52W High: ${stats_52w['52_week_high']:.2f}")
                    st.write(f"52W Low: ${stats_52w['52_week_low']:.2f}")
                    st.write(f"From High: {stats_52w['pct_from_high']:.2f}%")

    except ValueError as e:
        st.error(f"Error: {str(e)}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        st.exception(e)
