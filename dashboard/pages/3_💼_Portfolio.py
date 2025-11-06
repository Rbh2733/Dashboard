"""
Portfolio Tracker Page

Track your portfolio:
- Holdings and performance
- Allocation analysis
- Compare vs benchmarks
- P/L tracking
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data.data_fetcher import fetch_multiple_tickers
from src.portfolio.tracker import (
    calculate_portfolio_value,
    calculate_portfolio_performance,
    calculate_allocation,
    compare_to_benchmark
)

st.set_page_config(page_title="Portfolio Tracker", page_icon="💼", layout="wide")

st.title("💼 Portfolio Tracker")
st.markdown("Track your holdings, performance, and allocation")

# Sidebar
with st.sidebar:
    st.header("Portfolio Input")

    input_method = st.radio(
        "Input Method",
        options=["CSV File", "Manual Entry"],
        index=1
    )

    if input_method == "CSV File":
        st.info("Upload a CSV file with columns: ticker, shares, purchase_price, purchase_date")
        uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])

        if uploaded_file is not None:
            try:
                portfolio_df = pd.read_csv(uploaded_file)
                st.success(f"✅ Loaded {len(portfolio_df)} holdings")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
                portfolio_df = None
        else:
            portfolio_df = None

    else:  # Manual Entry
        st.markdown("Enter your holdings below:")

        # Initialize session state for holdings
        if 'holdings' not in st.session_state:
            st.session_state.holdings = []

        # Input form
        with st.form("add_holding"):
            col1, col2 = st.columns(2)

            with col1:
                ticker = st.text_input("Ticker", value="AAPL")
                shares = st.number_input("Shares", min_value=0.0, value=10.0, step=1.0)

            with col2:
                purchase_price = st.number_input("Purchase Price", min_value=0.0, value=150.0, step=1.0)
                purchase_date = st.date_input("Purchase Date")

            submitted = st.form_submit_button("Add Holding")

            if submitted and ticker and shares > 0:
                st.session_state.holdings.append({
                    'ticker': ticker.upper(),
                    'shares': shares,
                    'purchase_price': purchase_price,
                    'purchase_date': str(purchase_date)
                })
                st.success(f"Added {ticker}")

        # Show current holdings
        if st.session_state.holdings:
            st.markdown("**Current Holdings:**")
            for i, holding in enumerate(st.session_state.holdings):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(f"{holding['ticker']}: {holding['shares']} @ ${holding['purchase_price']}")
                with col2:
                    if st.button("❌", key=f"del_{i}"):
                        st.session_state.holdings.pop(i)
                        st.rerun()

            if st.button("Clear All", type="secondary"):
                st.session_state.holdings = []
                st.rerun()

            portfolio_df = pd.DataFrame(st.session_state.holdings)
        else:
            portfolio_df = None

    benchmark_ticker = st.selectbox(
        "Benchmark",
        options=["SPY", "QQQ", "DIA", "IWM"],
        index=0
    )

    analyze_button = st.button("📊 Analyze Portfolio", type="primary", use_container_width=True)

# Main content
if analyze_button and portfolio_df is not None and len(portfolio_df) > 0:
    try:
        with st.spinner("Fetching current prices..."):
            # Get current prices
            tickers = portfolio_df['ticker'].unique().tolist()
            price_data = fetch_multiple_tickers(tickers, period='1y', interval='1d')

            if not price_data:
                st.error("Could not fetch price data for any tickers.")
                st.stop()

            # Calculate current prices
            current_prices = {}
            for ticker, df in price_data.items():
                if not df.empty:
                    current_prices[ticker] = df['Close'].iloc[-1]

            # Add current prices to portfolio
            portfolio_df['current_price'] = portfolio_df['ticker'].map(current_prices)

            # Calculate metrics
            portfolio_df['cost_basis'] = portfolio_df['shares'] * portfolio_df['purchase_price']
            portfolio_df['current_value'] = portfolio_df['shares'] * portfolio_df['current_price']
            portfolio_df['gain_loss'] = portfolio_df['current_value'] - portfolio_df['cost_basis']
            portfolio_df['gain_loss_pct'] = (portfolio_df['gain_loss'] / portfolio_df['cost_basis']) * 100

            # Overall metrics
            total_cost = portfolio_df['cost_basis'].sum()
            total_value = portfolio_df['current_value'].sum()
            total_gain_loss = total_value - total_cost
            total_gain_loss_pct = (total_gain_loss / total_cost) * 100

            # Display summary
            st.markdown("---")
            st.subheader("Portfolio Summary")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Value", f"${total_value:,.2f}")

            with col2:
                st.metric("Cost Basis", f"${total_cost:,.2f}")

            with col3:
                st.metric(
                    "Total Gain/Loss",
                    f"${total_gain_loss:,.2f}",
                    f"{total_gain_loss_pct:+.2f}%"
                )

            with col4:
                st.metric("Holdings", len(portfolio_df))

            st.markdown("---")

            # Holdings table
            st.subheader("Holdings Detail")

            display_df = portfolio_df[[
                'ticker', 'shares', 'purchase_price', 'current_price',
                'cost_basis', 'current_value', 'gain_loss', 'gain_loss_pct'
            ]].copy()

            # Format columns
            display_df['purchase_price'] = display_df['purchase_price'].apply(lambda x: f"${x:.2f}")
            display_df['current_price'] = display_df['current_price'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")
            display_df['cost_basis'] = display_df['cost_basis'].apply(lambda x: f"${x:,.2f}")
            display_df['current_value'] = display_df['current_value'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")
            display_df['gain_loss'] = display_df['gain_loss'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")
            display_df['gain_loss_pct'] = display_df['gain_loss_pct'].apply(lambda x: f"{x:+.2f}%" if pd.notna(x) else "N/A")

            st.dataframe(display_df, use_container_width=True)

            st.markdown("---")

            # Allocation pie chart
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Portfolio Allocation")

                fig = px.pie(
                    portfolio_df,
                    values='current_value',
                    names='ticker',
                    title='Holdings by Value'
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Gain/Loss by Holding")

                fig = go.Figure()
                colors = ['green' if x >= 0 else 'red' for x in portfolio_df['gain_loss']]

                fig.add_trace(go.Bar(
                    x=portfolio_df['ticker'],
                    y=portfolio_df['gain_loss'],
                    marker_color=colors,
                    text=portfolio_df['gain_loss_pct'].apply(lambda x: f"{x:+.1f}%"),
                    textposition='outside'
                ))

                fig.update_layout(
                    title='Gain/Loss by Position',
                    xaxis_title='Ticker',
                    yaxis_title='Gain/Loss ($)',
                    showlegend=False
                )

                st.plotly_chart(fig, use_container_width=True)

            # Performance comparison
            st.markdown("---")
            st.subheader(f"Portfolio vs {benchmark_ticker}")

            with st.spinner(f"Comparing to {benchmark_ticker}..."):
                try:
                    benchmark_data = fetch_multiple_tickers([benchmark_ticker], period='1y', interval='1d')

                    if benchmark_ticker in benchmark_data:
                        benchmark_df = benchmark_data[benchmark_ticker]

                        # Calculate portfolio historical value (simplified)
                        # For a proper calculation, would need to track over time
                        st.info("Note: Detailed historical portfolio performance tracking requires transaction history over time.")

                        # Show benchmark performance
                        bench_start = benchmark_df['Close'].iloc[0]
                        bench_end = benchmark_df['Close'].iloc[-1]
                        bench_return = ((bench_end - bench_start) / bench_start) * 100

                        col1, col2 = st.columns(2)

                        with col1:
                            st.metric(
                                "Portfolio Return",
                                f"{total_gain_loss_pct:+.2f}%"
                            )

                        with col2:
                            st.metric(
                                f"{benchmark_ticker} 1Y Return",
                                f"{bench_return:+.2f}%"
                            )

                        # Show benchmark chart
                        fig = go.Figure()

                        fig.add_trace(go.Scatter(
                            x=benchmark_df.index,
                            y=benchmark_df['Close'],
                            name=benchmark_ticker,
                            line=dict(color='blue', width=2)
                        ))

                        fig.update_layout(
                            title=f"{benchmark_ticker} - 1 Year Performance",
                            xaxis_title="Date",
                            yaxis_title="Price ($)",
                            hovermode='x unified'
                        )

                        st.plotly_chart(fig, use_container_width=True)

                except Exception as e:
                    st.warning(f"Could not fetch benchmark data: {str(e)}")

    except Exception as e:
        st.error(f"Error analyzing portfolio: {str(e)}")
        st.exception(e)

elif analyze_button:
    st.warning("Please add some holdings to your portfolio first.")

else:
    # Initial state
    st.info("👆 Add your holdings in the sidebar and click 'Analyze Portfolio' to see your performance.")

    st.markdown("---")
    st.subheader("Getting Started")

    st.markdown("""
    ### How to use the Portfolio Tracker:

    1. **Choose Input Method:**
       - **Manual Entry:** Add holdings one by one using the form
       - **CSV Upload:** Upload a CSV file with your holdings

    2. **CSV Format:**
       Your CSV should have these columns:
       - `ticker`: Stock symbol (e.g., AAPL)
       - `shares`: Number of shares owned
       - `purchase_price`: Price per share at purchase
       - `purchase_date`: When you bought it (YYYY-MM-DD)

    3. **Example CSV:**
       ```
       ticker,shares,purchase_price,purchase_date
       AAPL,10,150.00,2024-01-15
       MSFT,5,350.00,2024-02-01
       SPY,20,450.00,2024-01-10
       ```

    4. **Analyze:**
       - Click "Analyze Portfolio" to see your performance
       - View allocation, gains/losses, and benchmark comparison

    ### Download Template
    """)

    template_df = pd.DataFrame({
        'ticker': ['AAPL', 'MSFT', 'SPY'],
        'shares': [10, 5, 20],
        'purchase_price': [150.00, 350.00, 450.00],
        'purchase_date': ['2024-01-15', '2024-02-01', '2024-01-10']
    })

    csv_template = template_df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV Template",
        data=csv_template,
        file_name="portfolio_template.csv",
        mime="text/csv"
    )
