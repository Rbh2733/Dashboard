"""
Financial Dashboard - Main Application

A comprehensive financial analysis dashboard with:
- Stock/ETF analysis with technical indicators
- Market scanner for breakout opportunities
- Portfolio tracking and performance analysis
- Options analysis and strategy modeling
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Financial Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main page
def main():
    st.title("📈 Financial Dashboard")
    st.markdown("---")

    st.markdown("""
    ## Welcome to Your Financial Analysis Dashboard

    This dashboard provides comprehensive tools for financial analysis:

    ### 📊 **Stock/ETF Analyzer**
    - Interactive price charts with technical indicators
    - Fundamental analysis and financial metrics
    - Pattern recognition and signals
    - Support/resistance levels

    ### 🔍 **Market Scanner**
    - Scan for breakout opportunities
    - High volume movers
    - RSI extremes (oversold/overbought)
    - Golden/Death cross signals
    - Stocks near 52-week highs

    ### 💼 **Portfolio Tracker**
    - Track your holdings and performance
    - Portfolio allocation analysis
    - Compare against benchmarks (SPY, QQQ)
    - Risk metrics and diversification

    ### 🎯 **Options Analysis** *(Coming Soon)*
    - Options chain viewer
    - Greeks calculator
    - Strategy P/L modeling
    - Covered calls, spreads, and more

    ---

    ### 🚀 Get Started
    Use the sidebar navigation to explore different features of the dashboard.

    ### 📝 Notes
    - Data is fetched from Yahoo Finance (yfinance)
    - All analysis is quantitative and reproducible
    - Technical indicators are calculated using pandas/numpy
    - This is for educational purposes only - not financial advice

    """)

    # Sidebar info
    with st.sidebar:
        st.markdown("### About")
        st.info("""
        This dashboard uses:
        - **yfinance** for market data
        - **pandas/numpy** for analysis
        - **plotly** for interactive charts
        - **streamlit** for the interface

        Built with Python 3.10+
        """)

        st.markdown("### Quick Links")
        st.markdown("""
        - [Stock Analyzer](Analyzer)
        - [Market Scanner](Scanner)
        - [Portfolio Tracker](Portfolio)
        """)


if __name__ == "__main__":
    main()
