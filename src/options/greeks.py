"""
Options Greeks Module

Calculate and explain the options Greeks:
- Delta: Rate of change in option price relative to stock price
- Gamma: Rate of change in delta relative to stock price
- Theta: Rate of time decay
- Vega: Sensitivity to implied volatility changes
- Rho: Sensitivity to interest rate changes

Uses Black-Scholes model for calculations.
"""

import numpy as np
from scipy.stats import norm
from typing import Dict, Optional
from datetime import datetime, date


def calculate_time_to_expiration(expiration_date: str) -> float:
    """
    Calculate time to expiration in years.

    Args:
        expiration_date: Expiration date string (YYYY-MM-DD)

    Returns:
        float: Time to expiration in years
    """
    if isinstance(expiration_date, str):
        exp_date = datetime.strptime(expiration_date, '%Y-%m-%d').date()
    else:
        exp_date = expiration_date

    today = date.today()
    days_to_expiration = (exp_date - today).days

    # Convert to years
    return max(days_to_expiration / 365.0, 0.001)  # Minimum to avoid division issues


def black_scholes_call(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float
) -> float:
    """
    Calculate Black-Scholes price for a call option.

    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free interest rate
        sigma: Implied volatility (annualized)

    Returns:
        float: Call option theoretical price
    """
    if T <= 0:
        return max(S - K, 0)

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

    return call_price


def black_scholes_put(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float
) -> float:
    """
    Calculate Black-Scholes price for a put option.

    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free interest rate
        sigma: Implied volatility (annualized)

    Returns:
        float: Put option theoretical price
    """
    if T <= 0:
        return max(K - S, 0)

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    return put_price


def calculate_delta(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str = 'call'
) -> float:
    """
    Calculate Delta.

    Delta measures the rate of change of option price with respect to stock price.
    - Call Delta: 0 to 1
    - Put Delta: -1 to 0

    Interpretation:
    - Delta of 0.5 means option price moves $0.50 for every $1 move in stock
    - ITM options have delta closer to 1 (calls) or -1 (puts)
    - OTM options have delta closer to 0

    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free interest rate
        sigma: Implied volatility
        option_type: 'call' or 'put'

    Returns:
        float: Delta value
    """
    if T <= 0:
        if option_type == 'call':
            return 1.0 if S > K else 0.0
        else:
            return -1.0 if S < K else 0.0

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    if option_type == 'call':
        delta = norm.cdf(d1)
    else:  # put
        delta = norm.cdf(d1) - 1

    return delta


def calculate_gamma(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float
) -> float:
    """
    Calculate Gamma.

    Gamma measures the rate of change of delta with respect to stock price.
    Gamma is the same for calls and puts.

    Interpretation:
    - Higher gamma means delta changes more rapidly
    - ATM options have highest gamma
    - Gamma is highest near expiration

    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free interest rate
        sigma: Implied volatility

    Returns:
        float: Gamma value
    """
    if T <= 0:
        return 0

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))

    return gamma


def calculate_theta(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str = 'call'
) -> float:
    """
    Calculate Theta (per day).

    Theta measures the rate of time decay of the option value.
    Theta is typically negative (options lose value as time passes).

    Interpretation:
    - Theta of -0.05 means option loses $0.05 in value per day
    - ATM options have highest theta
    - Theta accelerates as expiration approaches

    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free interest rate
        sigma: Implied volatility
        option_type: 'call' or 'put'

    Returns:
        float: Theta value (per day)
    """
    if T <= 0:
        return 0

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == 'call':
        theta = (
            -S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
            - r * K * np.exp(-r * T) * norm.cdf(d2)
        )
    else:  # put
        theta = (
            -S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
            + r * K * np.exp(-r * T) * norm.cdf(-d2)
        )

    # Convert to per-day theta
    theta_per_day = theta / 365

    return theta_per_day


def calculate_vega(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float
) -> float:
    """
    Calculate Vega.

    Vega measures sensitivity to changes in implied volatility.
    Vega is the same for calls and puts.

    Interpretation:
    - Vega of 0.10 means option price changes by $0.10 for 1% change in IV
    - ATM options have highest vega
    - Longer-dated options have higher vega

    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free interest rate
        sigma: Implied volatility

    Returns:
        float: Vega value (per 1% change in IV)
    """
    if T <= 0:
        return 0

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    vega = S * norm.pdf(d1) * np.sqrt(T)

    # Convert to per 1% change
    vega = vega / 100

    return vega


def calculate_rho(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str = 'call'
) -> float:
    """
    Calculate Rho.

    Rho measures sensitivity to changes in interest rates.

    Interpretation:
    - Rho of 0.05 means option price changes by $0.05 for 1% change in rates
    - Call rho is positive (higher rates increase call value)
    - Put rho is negative (higher rates decrease put value)

    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free interest rate
        sigma: Implied volatility
        option_type: 'call' or 'put'

    Returns:
        float: Rho value (per 1% change in interest rate)
    """
    if T <= 0:
        return 0

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == 'call':
        rho = K * T * np.exp(-r * T) * norm.cdf(d2)
    else:  # put
        rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)

    # Convert to per 1% change
    rho = rho / 100

    return rho


def calculate_all_greeks(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str = 'call'
) -> Dict[str, float]:
    """
    Calculate all Greeks at once.

    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free interest rate
        sigma: Implied volatility
        option_type: 'call' or 'put'

    Returns:
        dict: All Greeks values
    """
    greeks = {
        'delta': calculate_delta(S, K, T, r, sigma, option_type),
        'gamma': calculate_gamma(S, K, T, r, sigma),
        'theta': calculate_theta(S, K, T, r, sigma, option_type),
        'vega': calculate_vega(S, K, T, r, sigma),
        'rho': calculate_rho(S, K, T, r, sigma, option_type)
    }

    # Add theoretical price
    if option_type == 'call':
        greeks['theoretical_price'] = black_scholes_call(S, K, T, r, sigma)
    else:
        greeks['theoretical_price'] = black_scholes_put(S, K, T, r, sigma)

    return greeks


def explain_greeks() -> Dict[str, str]:
    """
    Return explanations of each Greek.

    Returns:
        dict: Explanations of each Greek
    """
    return {
        'Delta': """
        **Delta (Δ)**: Rate of change in option price per $1 change in stock price
        - Call Delta: 0 to 1 | Put Delta: -1 to 0
        - Delta of 0.50 means option moves $0.50 for every $1 stock move
        - ITM options have higher delta (closer to 1 or -1)
        - Can also represent probability of expiring ITM
        """,

        'Gamma': """
        **Gamma (Γ)**: Rate of change in Delta per $1 change in stock price
        - Same for calls and puts
        - Higher gamma means Delta changes more rapidly
        - ATM options have highest gamma
        - Increases as expiration approaches
        """,

        'Theta': """
        **Theta (Θ)**: Rate of time decay per day
        - Usually negative (options lose value over time)
        - Theta of -0.05 means option loses $0.05 per day
        - ATM options have highest theta
        - Accelerates near expiration
        - Option sellers benefit from theta decay
        """,

        'Vega': """
        **Vega (ν)**: Sensitivity to 1% change in implied volatility
        - Same for calls and puts
        - Vega of 0.10 means $0.10 change per 1% IV change
        - ATM options have highest vega
        - Longer-dated options more sensitive to IV
        - Higher IV = higher option prices
        """,

        'Rho': """
        **Rho (ρ)**: Sensitivity to 1% change in interest rates
        - Call rho is positive | Put rho is negative
        - Usually least impactful Greek
        - More significant for long-dated options
        - Higher rates increase call value, decrease put value
        """
    }
