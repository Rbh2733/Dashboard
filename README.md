# 📈 Financial Dashboard

A comprehensive Python-based financial analysis dashboard for analyzing stocks, ETFs, and options. Built with Streamlit, featuring technical analysis, market scanning, portfolio tracking, and options analytics.

## 🎯 Features

### 1. Stock/ETF Analyzer 📊
- **Interactive Charts**: Candlestick charts with volume using Plotly
- **Technical Indicators**:
  - Moving Averages (SMA 20/50/200, EMA)
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands
  - VWAP (Volume Weighted Average Price)
  - OBV (On-Balance Volume)
- **Fundamental Analysis**: P/E, P/S, P/B, ROE, margins, growth metrics
- **Pattern Recognition**: Doji, Engulfing, Hammer, Shooting Star, Consolidation
- **Support/Resistance Levels**
- **52-Week High/Low Analysis**

### 2. Market Scanner 🔍
- **Breakout Candidates**: Multi-signal composite scoring
- **High Volume Movers**: Relative volume > 2x average
- **Oversold Stocks**: RSI < 30
- **Golden Cross**: 50-day SMA crosses above 200-day SMA
- **Custom Scans**: Define your own criteria
- **Export Results**: Download scan results as CSV
- Scan S&P 500 sample, ETFs, or custom ticker lists

### 3. Portfolio Tracker 💼
- **Holdings Management**: Manual entry or CSV upload
- **Performance Tracking**: Real-time P/L and returns
- **Allocation Analysis**: Interactive pie charts
- **Benchmark Comparison**: Compare vs SPY, QQQ, DIA, IWM
- **Position-Level Metrics**: Gain/loss per holding
- **Risk Metrics**: Beta, Sharpe ratio, max drawdown calculations

### 4. Options Analysis 🎯
- **Options Chains**: Fetch calls and puts for any expiration
- **Options Greeks**:
  - Delta: Price sensitivity
  - Gamma: Delta sensitivity
  - Theta: Time decay
  - Vega: IV sensitivity
  - Rho: Interest rate sensitivity
- **Black-Scholes Pricing**: Theoretical option valuation
- **Liquidity Filtering**: Volume and open interest filters
- **Moneyness Filters**: ATM, ITM, OTM options

## 📁 Project Structure

```
financial_dashboard/
├── src/
│   ├── data/
│   │   └── data_fetcher.py          # yfinance data retrieval
│   ├── analysis/
│   │   ├── technical.py             # Technical indicators
│   │   ├── fundamental.py           # Fundamental metrics & DCF
│   │   └── patterns.py              # Chart & candlestick patterns
│   ├── scanner/
│   │   └── breakout_scanner.py      # Market scanning functions
│   ├── options/
│   │   ├── chains.py                # Options chain retrieval
│   │   └── greeks.py                # Greeks calculations
│   └── portfolio/
│       └── tracker.py               # Portfolio analytics
├── dashboard/
│   ├── app.py                       # Main Streamlit app
│   └── pages/
│       ├── 1_📊_Analyzer.py         # Stock analyzer page
│       ├── 2_🔍_Scanner.py          # Market scanner page
│       └── 3_💼_Portfolio.py        # Portfolio tracker page
├── tests/                           # Unit tests (pytest)
├── data/                            # Data files (CSV)
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd Dashboard
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the dashboard**
```bash
streamlit run dashboard/app.py
```

The dashboard will open in your default web browser at `http://localhost:8501`

## 📚 Usage Guide

### Stock/ETF Analyzer

1. Navigate to the **Analyzer** page
2. Enter a ticker symbol (e.g., AAPL, SPY)
3. Select time period (1mo to 5y)
4. Choose technical indicators to display
5. Toggle RSI/MACD subplots
6. View results in:
   - **Price Chart**: Interactive candlesticks with indicators
   - **Technical Summary**: Indicator values and signals
   - **Fundamentals**: Valuation, profitability, growth metrics
   - **Patterns**: Candlestick patterns and chart analysis

### Market Scanner

1. Navigate to the **Scanner** page
2. Select scan type:
   - Breakout Candidates (composite scoring)
   - High Volume Movers
   - Oversold Stocks
   - Golden Cross
   - Custom Scan (define your own filters)
3. Choose ticker list (S&P 500 sample, ETFs, or custom)
4. Click "Run Scan"
5. View results in sortable table
6. Export to CSV

### Portfolio Tracker

1. Navigate to the **Portfolio** page
2. Add holdings:
   - **Manual Entry**: Use the form to add positions
   - **CSV Upload**: Upload a CSV file (see template)
3. Click "Analyze Portfolio"
4. View:
   - Total value, cost basis, and P/L
   - Holdings detail table
   - Allocation pie chart
   - Gain/loss by position
   - Benchmark comparison

**CSV Format:**
```csv
ticker,shares,purchase_price,purchase_date
AAPL,10,150.00,2024-01-15
MSFT,5,350.00,2024-02-01
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/analysis/test_technical.py -v
```

**Test Coverage:**
- Data Fetcher: 17 tests
- Technical Analysis: 19 tests (all passing)
- Breakout Scanner: 9 tests (all passing)
- Pattern Recognition: Integrated in technical tests

## 🔧 Technical Details

### Technical Indicators
All technical indicators are implemented from scratch using pandas and numpy for full transparency and learning:

- **SMA/EMA**: Simple and Exponential Moving Averages
- **RSI**: Relative Strength Index (14-period default)
- **MACD**: 12/26/9 configuration
- **Bollinger Bands**: 20-period, 2 std dev
- **VWAP**: Volume-weighted average price
- **OBV**: On-Balance Volume

### Fundamental Metrics
Extracted from yfinance:
- Valuation: P/E, P/S, P/B, PEG ratios
- Profitability: ROE, ROA, margins
- Financial Health: Debt ratios, current ratio, FCF
- Growth: Revenue and earnings growth
- DCF Calculator: Simple discounted cash flow model

### Options Greeks
Black-Scholes model implementation using scipy:
- **Delta**: First derivative of price w.r.t. stock price
- **Gamma**: Second derivative (delta sensitivity)
- **Theta**: Time decay (per day)
- **Vega**: IV sensitivity (per 1%)
- **Rho**: Interest rate sensitivity (per 1%)

## 📊 Data Source

- **Market Data**: Yahoo Finance via yfinance
- **Update Frequency**: Real-time during market hours (with ~15min delay)
- **Historical Data**: Up to max available history per ticker
- **Options Data**: Real-time options chains and Greeks

## ⚠️ Important Notes

1. **Educational Purpose**: This dashboard is for educational and research purposes only, not financial advice
2. **Data Accuracy**: Data is sourced from Yahoo Finance and may have delays or inaccuracies
3. **No Trading**: This tool does not execute trades
4. **Risk Disclaimer**: Past performance does not guarantee future results

## 🛠️ Development

### Adding New Features

The modular structure makes it easy to add new features:

1. **New Indicators**: Add to `src/analysis/technical.py`
2. **New Scans**: Add to `src/scanner/breakout_scanner.py`
3. **New Dashboard Pages**: Create in `dashboard/pages/`
4. **New Tests**: Add to corresponding `tests/` subdirectory

### Code Style

- Follow TDD (Test-Driven Development) principles
- Write tests before implementation
- Document all functions with docstrings
- Use type hints for function parameters
- Keep functions modular and single-purpose

## 📝 Dependencies

**Core:**
- pandas >= 2.0.0
- numpy >= 1.24.0
- scipy >= 1.10.0
- yfinance >= 0.2.28

**Visualization:**
- plotly >= 5.14.0
- streamlit >= 1.28.0
- matplotlib >= 3.7.0

**Testing:**
- pytest >= 7.4.0
- pytest-cov >= 4.1.0

See `requirements.txt` for complete list.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is for educational purposes. Use at your own risk.

## 🙋 Support

For issues, questions, or suggestions:
- Create an issue on GitHub
- Review the code documentation
- Check test files for usage examples

## 🎓 Learning Resources

This dashboard is designed for learning. Key concepts covered:
- Technical analysis and indicators
- Financial statement analysis
- Options theory and Greeks
- Portfolio management
- Quantitative finance
- Data visualization
- Python financial libraries

## 🔮 Future Enhancements

Potential additions:
- [ ] Backtesting engine for strategies
- [ ] Options strategy P/L modeling
- [ ] Real-time alerts and notifications
- [ ] Machine learning price predictions
- [ ] Correlation analysis
- [ ] Sector rotation analysis
- [ ] Earnings calendar integration
- [ ] News sentiment analysis

---

**Built with Python 🐍 | Streamlit | Plotly | pandas**

*Not financial advice. For educational purposes only.*
