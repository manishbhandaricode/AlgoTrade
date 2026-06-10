import math
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def norm_cdf(x: float) -> float:
    """
    Standard normal cumulative distribution function (CDF) using math.erf.
    Ensures zero external dependency (no scipy required).
    """
    try:
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))
    except (ValueError, OverflowError):
        return 1.0 if x > 0 else 0.0

def calculate_black_scholes(S: float, K: float, T: float, r: float, sigma: float, option_type: str = 'CE') -> tuple[float, float]:
    """
    Calculates the theoretical Black-Scholes-Merton option premium and delta.
    option_type: 'CE' for Call Option, 'PE' for Put Option.
    T: Time to maturity in years (days_to_expiry / 365).
    """
    # Prevent division by zero or negative time
    T = max(T, 0.0001)
    sigma = max(sigma, 0.01)
    
    try:
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        
        if option_type == 'CE':
            premium = S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
            delta = norm_cdf(d1)
        elif option_type == 'PE':
            premium = K * math.exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1)
            delta = norm_cdf(d1) - 1.0
        else:
            raise ValueError("option_type must be either 'CE' or 'PE'")
            
        return max(premium, 0.05), round(delta, 3)
    except Exception:
        return 0.05, 0.0

def estimate_historical_volatility(df: pd.DataFrame, window: int = 30) -> float:
    """
    Estimates annualized historical volatility from historical daily Close prices.
    Returns volatility as a decimal (e.g. 0.15 for 15%).
    """
    if len(df) < window:
        return 0.15  # Fallback default (15% standard index volatility)
    
    close = df['Close'].tail(window)
    log_returns = np.log(close / close.shift(1)).dropna()
    daily_std = np.std(log_returns)
    annualized_vol = daily_std * math.sqrt(252)
    return max(annualized_vol, 0.05)

def get_next_expiry_date(from_date: datetime, expiry_day: int = 3) -> datetime:
    """
    Finds the next expiry date.
    expiry_day: 3 for Thursday (Standard Nifty weekly expiry).
    """
    days_ahead = expiry_day - from_date.weekday()
    if days_ahead <= 0:  # If today is past/on the expiry day, look to next week
        days_ahead += 7
    return from_date + timedelta(days_ahead)

def generate_simulated_option_chain(spot_price: float, iv: float, strikes_count: int = 10, strike_interval: int = 50, days_to_expiry: int = 5, r: float = 0.065) -> pd.DataFrame:
    """
    Generates a simulated option chain around the current spot price.
    """
    # Find ATM Strike
    atm_strike = round(spot_price / strike_interval) * strike_interval
    
    strikes = []
    start_strike = atm_strike - (strikes_count // 2) * strike_interval
    for i in range(strikes_count):
        strikes.append(start_strike + i * strike_interval)
        
    T = days_to_expiry / 365.0
    
    rows = []
    for K in strikes:
        ce_premium, ce_delta = calculate_black_scholes(spot_price, K, T, r, iv, 'CE')
        pe_premium, pe_delta = calculate_black_scholes(spot_price, K, T, r, iv, 'PE')
        
        rows.append({
            'Strike': K,
            'CE_Premium': round(ce_premium, 2),
            'CE_Delta': ce_delta,
            'PE_Premium': round(pe_premium, 2),
            'PE_Delta': pe_delta,
            'Type': 'ATM' if K == atm_strike else ('ITM (CE) / OTM (PE)' if K < atm_strike else 'OTM (CE) / ITM (PE)')
        })
        
    return pd.DataFrame(rows)
