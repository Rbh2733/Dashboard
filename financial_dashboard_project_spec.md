# Financial Dashboard Project Specification

## Project Overview

Build a high-performance financial dashboard using Python with three primary functions:

1. **Market Analysis**: Analyze individual stocks and ETFs using technical and fundamental data
2. **Market Scanning**: Discover equities showing pre-breakout signals or unusual momentum
3. **Portfolio Tracking**: Track performance, allocation, and risk metrics of personal investments and options positions

**Core Principle**: All analysis must be quantitative, reproducible, and clearly explained.

---

## Key Technologies & Libraries

- **Language**: Python 3.10+
- **Data Analysis**: pandas, numpy
- **Data Visualization**: Plotly (preferred for interactive charts), matplotlib
- **Dashboard Framework**: Streamlit (preferred for rapid development) or Dash
- **Financial Data API**: yfinance (for EOD data, options chains, and fundamental data)
- **Technical Analysis**: pandas-ta (preferred)
- **Testing**: pytest

---

## Core Focus Areas

### Asset Types
- **Equities**: General equities across all sectors, with focus on US markets
- **ETFs**: Broad market (SPY, QQQ) and thematic/sector ETFs

### Key Capabilities
- **Scanning & Breakout Discovery**: Identify equities showing pre-breakout patterns (volume surges, consolidation, key indicator crossovers)
- **Options Strategy Analysis**: Model and backtest options strategies (covered calls, cash-secured puts, vertical spreads) with emphasis on understanding the Greeks

---

## Core Analysis Techniques

### Technical Analysis (Key Learning Area)

**Indicators**:
- RSI, MACD, Bollinger Bands
- Moving Averages (SMA/EMA)
- VWAP
- On-Balance Volume (OBV)

**Pattern Recognition**:
- Algorithmic identification of chart patterns (Head & Shoulders, Flags, Triangles)
- Candlestick patterns

**Volume Analysis**:
- Relative volume
- Volume profile
- Accumulation/distribution

**Support/Resistance**:
- Automated plotting of S/R levels

### Fundamental Analysis

**Core Metrics**:
- P/E, P/S, P/B, EPS, FCF
- Dividend Yield, PEG Ratio

**Financial Statements**:
- Income Statement, Balance Sheet, Cash Flow analysis
- Revenue growth, debt-to-equity

**Valuation**:
- Build tools for basic Discounted Cash Flow (DCF) models

### Portfolio Analysis
- P/L tracking
- Allocation analysis
- Beta calculation
- Performance vs. benchmarks

---

## Roles & Responsibilities

### My Role (User)
- Project lead and chief analyst
- Set strategic direction and define analytical models
- Provide specific backtesting parameters
- Challenge assumptions
- Analytical, data-driven, focused on building robust custom framework

### Claude's Role
- Expert-level AI assistant specializing in:
  - Data Science
  - Financial Analysis
  - Python application development
- Help write, debug, optimize, and test code
- Follow all instructions and coding standards in this document

---

## Core Tasks & Instructions

### 1. Development Process

**TDD First**:
- For all new backend functions, write pytest unit tests first
- State the tests, confirm they will fail, then write code to make them pass

**Planning**:
- Before writing new pages, modules, or complex functions, present step-by-step plan
- Include: files to create, functions to write, data flow
- **DO NOT write code until plan is approved**

**Modularity**:
- Separate data fetching, analysis logic, and dashboard UI code
- Use different functions and files

### 2. Equity & ETF Analysis Functions

Build functions to:
- Fetch historical price/volume data for any list of tickers
- Calculate comprehensive technical indicators using pandas-ta
- **NEW**: Programmatically identify chart patterns (consolidation) and candlestick patterns (doji, engulfing)
- **NEW**: Fetch financial statements (Income, Balance, Cash Flow) using yfinance and display cleanly
- **NEW**: Build simple DCF calculator module with input assumptions (growth rate, terminal rate) for valuation
- Run simple backtests on strategies (e.g., "buy on golden cross, sell on death cross")

### 3. Breakout Scanner Module

Build market scanning module:

**Task**: Create functions to scan ticker lists (e.g., S&P 500) for specific technical signals

**Examples**:
- High relative volume
- RSI crossing 30 (oversold) or 70 (overbought)
- Golden/death cross events
- Stocks near 52-week highs
- Consolidation patterns

**Goal**: Create "shortlist" of stocks for further manual analysis

### 4. Options Analysis Module

**Key Learning Area**: Explanations as important as code

Build functions to:
1. Fetch and display clean options chains for given ticker
2. Calculate and clearly explain the "Greeks" (Delta, Theta, Vega, Gamma)
3. Model P/L graphs for strategies:
   - Example: "Show profit/loss for covered call at X strike"
   - Example: "Model bull call spread"

### 5. Dashboard Components

**Stock/ETF Analyzer Page**:
- Enter ticker to see interactive chart (Plotly)
- Selectable technical indicators
- Fundamental data
- Financial statements

**Market Scanner Page**:
- Display Breakout Scanner Module output
- Sortable table format

**Portfolio Tracker Page**:
- Read from CSV/JSON of holdings (ticker, shares, purchase_price)
- Calculate:
  - Total market value and P/L (total and per holding)
  - Portfolio allocation (pie chart)
  - Portfolio performance charted vs. benchmark (e.g., SPY)

---

## Important Rules (Guardrails)

⚠️ **CRITICAL SAFETY RULES**:

1. **IMPORTANT**: Do not write or modify any file outside of the current project directory

2. **IMPORTANT**: Always ask for permission before executing any shell command, especially:
   - `rm` (delete)
   - `mv` (move)
   - `git commit` (version control)

3. **IMPORTANT**: When asked to "undo" something, revert the last set of code changes

---

## Project Structure (To Be Developed)

```
financial_dashboard/
├── src/
│   ├── data/
│   │   └── data_fetcher.py
│   ├── analysis/
│   │   ├── technical.py
│   │   ├── fundamental.py
│   │   └── patterns.py
│   ├── scanner/
│   │   └── breakout_scanner.py
│   ├── options/
│   │   ├── chains.py
│   │   └── greeks.py
│   └── portfolio/
│       └── tracker.py
├── dashboard/
│   ├── pages/
│   │   ├── analyzer.py
│   │   ├── scanner.py
│   │   └── portfolio.py
│   └── app.py
├── tests/
│   └── (mirror src structure)
├── data/
│   └── portfolio.csv
└── requirements.txt
```

---

## Development Workflow

1. **Propose Plan** → Get Approval
2. **Write Tests** → Confirm They Fail
3. **Write Code** → Make Tests Pass
4. **Refactor** → Optimize and Clean
5. **Document** → Add docstrings and comments
6. **Integrate** → Connect to dashboard

---

## Next Steps

Ready to begin development when you provide direction on:
- Which module to start with
- Specific feature requirements
- Any clarifications needed
