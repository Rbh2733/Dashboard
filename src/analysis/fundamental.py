"""
Fundamental Analysis Module

Functions for analyzing company fundamentals and financial metrics.

Metrics included:
- Valuation ratios (P/E, P/S, P/B, PEG)
- Profitability metrics (EPS, ROE, ROA)
- Financial health (Debt-to-Equity, Current Ratio)
- Growth metrics
- DCF valuation
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional


def calculate_valuation_ratios(info: Dict) -> Dict:
    """
    Calculate key valuation ratios from ticker info.

    Args:
        info: Dictionary containing stock info from yfinance

    Returns:
        dict: Dictionary of valuation ratios
    """
    ratios = {}

    # Price-to-Earnings Ratio
    ratios['PE_Ratio'] = info.get('trailingPE', None) or info.get('forwardPE', None)

    # Price-to-Sales Ratio
    ratios['PS_Ratio'] = info.get('priceToSalesTrailing12Months', None)

    # Price-to-Book Ratio
    ratios['PB_Ratio'] = info.get('priceToBook', None)

    # PEG Ratio (P/E relative to growth)
    ratios['PEG_Ratio'] = info.get('pegRatio', None)

    # Enterprise Value multiples
    ratios['EV_to_Revenue'] = info.get('enterpriseToRevenue', None)
    ratios['EV_to_EBITDA'] = info.get('enterpriseToEbitda', None)

    return ratios


def calculate_profitability_metrics(info: Dict) -> Dict:
    """
    Calculate profitability metrics from ticker info.

    Args:
        info: Dictionary containing stock info from yfinance

    Returns:
        dict: Dictionary of profitability metrics
    """
    metrics = {}

    # Earnings Per Share
    metrics['EPS'] = info.get('trailingEps', None)

    # Return on Equity
    metrics['ROE'] = info.get('returnOnEquity', None)

    # Return on Assets
    metrics['ROA'] = info.get('returnOnAssets', None)

    # Profit Margins
    metrics['Gross_Margin'] = info.get('grossMargins', None)
    metrics['Operating_Margin'] = info.get('operatingMargins', None)
    metrics['Net_Margin'] = info.get('profitMargins', None)

    return metrics


def calculate_financial_health(info: Dict) -> Dict:
    """
    Calculate financial health metrics from ticker info.

    Args:
        info: Dictionary containing stock info from yfinance

    Returns:
        dict: Dictionary of financial health metrics
    """
    health = {}

    # Debt metrics
    health['Debt_to_Equity'] = info.get('debtToEquity', None)
    health['Total_Debt'] = info.get('totalDebt', None)
    health['Total_Cash'] = info.get('totalCash', None)

    # Liquidity ratios
    health['Current_Ratio'] = info.get('currentRatio', None)
    health['Quick_Ratio'] = info.get('quickRatio', None)

    # Free Cash Flow
    health['Free_Cash_Flow'] = info.get('freeCashflow', None)
    health['Operating_Cash_Flow'] = info.get('operatingCashflow', None)

    return health


def calculate_growth_metrics(info: Dict) -> Dict:
    """
    Calculate growth metrics from ticker info.

    Args:
        info: Dictionary containing stock info from yfinance

    Returns:
        dict: Dictionary of growth metrics
    """
    growth = {}

    # Revenue growth
    growth['Revenue_Growth'] = info.get('revenueGrowth', None)

    # Earnings growth
    growth['Earnings_Growth'] = info.get('earningsGrowth', None)
    growth['Quarterly_Earnings_Growth'] = info.get('earningsQuarterlyGrowth', None)

    # Revenue
    growth['Total_Revenue'] = info.get('totalRevenue', None)
    growth['Revenue_Per_Share'] = info.get('revenuePerShare', None)

    return growth


def get_dividend_metrics(info: Dict) -> Dict:
    """
    Extract dividend-related metrics from ticker info.

    Args:
        info: Dictionary containing stock info from yfinance

    Returns:
        dict: Dictionary of dividend metrics
    """
    dividends = {}

    dividends['Dividend_Yield'] = info.get('dividendYield', None)
    dividends['Dividend_Rate'] = info.get('dividendRate', None)
    dividends['Payout_Ratio'] = info.get('payoutRatio', None)
    dividends['Five_Year_Avg_Dividend_Yield'] = info.get('fiveYearAvgDividendYield', None)

    return dividends


def analyze_financial_statements(statements: Dict[str, pd.DataFrame]) -> Dict:
    """
    Analyze trends in financial statements.

    Args:
        statements: Dictionary with 'income_statement', 'balance_sheet', 'cash_flow' DataFrames

    Returns:
        dict: Dictionary of key insights and trends
    """
    analysis = {}

    income_stmt = statements.get('income_statement')
    balance_sheet = statements.get('balance_sheet')
    cash_flow = statements.get('cash_flow')

    # Analyze Income Statement
    if income_stmt is not None and not income_stmt.empty:
        if 'Total Revenue' in income_stmt.index:
            revenue = income_stmt.loc['Total Revenue']
            if len(revenue) > 1:
                # Calculate revenue growth (most recent vs previous)
                revenue_growth = ((revenue.iloc[0] - revenue.iloc[1]) / abs(revenue.iloc[1])) * 100
                analysis['Revenue_Growth_%'] = revenue_growth

        if 'Net Income' in income_stmt.index:
            net_income = income_stmt.loc['Net Income']
            if len(net_income) > 1:
                # Calculate earnings growth
                earnings_growth = ((net_income.iloc[0] - net_income.iloc[1]) / abs(net_income.iloc[1])) * 100
                analysis['Earnings_Growth_%'] = earnings_growth

    # Analyze Balance Sheet
    if balance_sheet is not None and not balance_sheet.empty:
        if 'Total Assets' in balance_sheet.index and 'Total Liabilities Net Minority Interest' in balance_sheet.index:
            total_assets = balance_sheet.loc['Total Assets'].iloc[0]
            total_liabilities = balance_sheet.loc['Total Liabilities Net Minority Interest'].iloc[0]
            analysis['Debt_to_Assets_Ratio'] = total_liabilities / total_assets if total_assets != 0 else None

    # Analyze Cash Flow
    if cash_flow is not None and not cash_flow.empty:
        if 'Free Cash Flow' in cash_flow.index:
            fcf = cash_flow.loc['Free Cash Flow']
            if len(fcf) > 1 and fcf.iloc[1] != 0:
                # Calculate FCF growth
                fcf_growth = ((fcf.iloc[0] - fcf.iloc[1]) / abs(fcf.iloc[1])) * 100
                analysis['FCF_Growth_%'] = fcf_growth

    return analysis


def simple_dcf_valuation(
    current_fcf: float,
    growth_rate: float = 0.10,
    terminal_growth_rate: float = 0.03,
    discount_rate: float = 0.10,
    projection_years: int = 5,
    shares_outstanding: float = 1.0
) -> Dict:
    """
    Calculate a simple Discounted Cash Flow (DCF) valuation.

    This is a simplified DCF model. Real DCF models should consider
    more factors and use detailed financial projections.

    Formula:
        1. Project FCF for N years using growth_rate
        2. Calculate terminal value using terminal_growth_rate
        3. Discount all cash flows to present value
        4. Divide by shares outstanding to get intrinsic value per share

    Args:
        current_fcf: Current free cash flow
        growth_rate: Expected FCF growth rate (default: 10%)
        terminal_growth_rate: Perpetual growth rate after projection period (default: 3%)
        discount_rate: Required rate of return/WACC (default: 10%)
        projection_years: Number of years to project (default: 5)
        shares_outstanding: Number of shares outstanding

    Returns:
        dict: DCF valuation results including intrinsic value per share
    """
    if current_fcf <= 0:
        return {
            'error': 'FCF must be positive for DCF valuation',
            'intrinsic_value_per_share': None
        }

    projected_fcf = []
    discounted_fcf = []

    # Project FCF and discount to present value
    for year in range(1, projection_years + 1):
        fcf = current_fcf * ((1 + growth_rate) ** year)
        pv = fcf / ((1 + discount_rate) ** year)
        projected_fcf.append(fcf)
        discounted_fcf.append(pv)

    # Calculate terminal value
    terminal_fcf = projected_fcf[-1] * (1 + terminal_growth_rate)
    terminal_value = terminal_fcf / (discount_rate - terminal_growth_rate)
    discounted_terminal_value = terminal_value / ((1 + discount_rate) ** projection_years)

    # Sum all present values
    enterprise_value = sum(discounted_fcf) + discounted_terminal_value

    # Calculate per-share value
    intrinsic_value_per_share = enterprise_value / shares_outstanding if shares_outstanding > 0 else None

    return {
        'enterprise_value': enterprise_value,
        'projected_fcf': projected_fcf,
        'sum_pv_fcf': sum(discounted_fcf),
        'terminal_value': terminal_value,
        'discounted_terminal_value': discounted_terminal_value,
        'intrinsic_value_per_share': intrinsic_value_per_share,
        'assumptions': {
            'growth_rate': growth_rate,
            'terminal_growth_rate': terminal_growth_rate,
            'discount_rate': discount_rate,
            'projection_years': projection_years
        }
    }


def create_fundamental_summary(info: Dict) -> Dict:
    """
    Create a comprehensive fundamental analysis summary.

    Args:
        info: Dictionary containing stock info from yfinance

    Returns:
        dict: Comprehensive dictionary of all fundamental metrics
    """
    summary = {}

    # Basic info
    summary['Company_Name'] = info.get('longName', info.get('shortName'))
    summary['Sector'] = info.get('sector')
    summary['Industry'] = info.get('industry')
    summary['Market_Cap'] = info.get('marketCap')
    summary['Current_Price'] = info.get('currentPrice', info.get('regularMarketPrice'))

    # Add all metric categories
    summary['Valuation'] = calculate_valuation_ratios(info)
    summary['Profitability'] = calculate_profitability_metrics(info)
    summary['Financial_Health'] = calculate_financial_health(info)
    summary['Growth'] = calculate_growth_metrics(info)
    summary['Dividends'] = get_dividend_metrics(info)

    return summary
