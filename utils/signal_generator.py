import pandas as pd
import numpy as np
from typing import Dict, Any
from utils.indicators import calculate_rsi, calculate_ichimoku, find_support_resistance_levels, calculate_daily_pivots
from utils.patterns import detect_candlestick_patterns

from utils.indicators import calculate_macd, calculate_bollinger_bands, calculate_moving_averages, calculate_atr

def generate_swing_blueprint(symbol: str, df: pd.DataFrame, strategy: str = "Ichimoku Trend") -> Dict[str, Any]:
    """
    Generates a swing trade plan based on 1D/1W closed bars using multiple strategies.
    Uses ATR for dynamic Stop Loss sizing.
    """
    if len(df) < 52:
        return {"decision": "NO TRADE", "reason": f"Insufficient data history.", "indicators": {}}
    
    df = df.copy()
    close_price = float(df['Close'].iloc[-1])
    
    # Calculate Core Indicators
    df['RSI'] = calculate_rsi(df)
    df['ATR'] = calculate_atr(df)
    ichimoku = calculate_ichimoku(df)
    macd = calculate_macd(df)
    bb = calculate_bollinger_bands(df)
    mas = calculate_moving_averages(df)
    patterns = detect_candlestick_patterns(df)
    
    df = pd.concat([df, ichimoku, macd, bb, mas, patterns], axis=1)
    supports, resistances = find_support_resistance_levels(df, window=15)
    
    valid_supports = [s for s in supports if s < close_price]
    nearest_support = valid_supports[-1] if valid_supports else (close_price * 0.95)
    
    valid_resistances = [r for r in resistances if r > close_price]
    nearest_resistance = valid_resistances[0] if valid_resistances else (close_price * 1.05)
    
    last_row = df.iloc[-1]
    atr_val = last_row['ATR'] if not pd.isna(last_row['ATR']) else (close_price * 0.02)
    
    decision = "HOLD"
    reason = "No active buy triggers based on the selected strategy."
    entry_price = round(close_price, 2)
    
    # --- STRATEGY 1: Ichimoku Trend (Default) ---
    if strategy == "Ichimoku Trend":
        above_cloud = False
        if not pd.isna(last_row['Senkou_A']) and not pd.isna(last_row['Senkou_B']):
            above_cloud = (close_price > last_row['Senkou_A']) and (close_price > last_row['Senkou_B'])
        trend_bullish = above_cloud and (close_price > last_row['Kijun'])
        if trend_bullish and last_row['RSI'] > 50:
            decision = "BUY"
            reason = "Structural bullish trend confirmed by Ichimoku and strong RSI momentum (>50)."
            
    # --- STRATEGY 2: Momentum Breakout ---
    elif strategy == "Momentum Breakout":
        ema_crossover = last_row['EMA_9'] > last_row['EMA_21']
        macd_bullish = last_row['Histogram'] > 0 and last_row['MACD'] > last_row['Signal']
        if ema_crossover and macd_bullish and last_row['RSI'] > 55:
            decision = "BUY"
            reason = "Momentum Breakout: EMA 9 crossed above EMA 21 with positive MACD divergence."
            
    # --- STRATEGY 3: Mean Reversion ---
    elif strategy == "Mean Reversion":
        at_lower_band = close_price <= (last_row['BB_Lower'] * 1.01)
        rsi_oversold = last_row['RSI'] < 35
        reversal_candle = last_row['Hammer'] | last_row['BullishEngulfing']
        if at_lower_band and (rsi_oversold or reversal_candle):
            decision = "BUY"
            reason = "Mean Reversion: Price rejected at lower Bollinger Band with oversold RSI or bullish pattern."
            entry_price = round(last_row['BB_Lower'], 2)

    # ATR Based Stop Loss (1.5x ATR for Swing)
    stop_loss = round(entry_price - (atr_val * 1.5), 2)
    target_price = round(nearest_resistance, 2)
    
    # If target is too close, calculate a mathematical target based on 2x Risk
    if target_price <= close_price * 1.01:
        target_price = round(entry_price + (atr_val * 3.0), 2)
        
    risk = entry_price - stop_loss
    reward = target_price - entry_price
    risk_reward = round(reward / risk, 2) if risk > 0 else 1.0
    
    if risk_reward < 1.0 and decision == "BUY":
        decision = "HOLD"
        reason = "Trade invalidated: Risk-to-Reward ratio is mathematically poor (< 1.0)."
    
    return {
        "symbol": symbol.upper(),
        "close_price": round(close_price, 2),
        "decision": decision,
        "reason": reason,
        "entry": entry_price,
        "stop_loss": stop_loss,
        "target": target_price,
        "risk_reward": risk_reward,
        "indicators": {
            "RSI": round(last_row['RSI'], 2),
            "ATR": round(atr_val, 2),
            "MACD": round(last_row.get('MACD', 0), 2),
            "NearestSupport": nearest_support,
            "NearestResistance": nearest_resistance
        }
    }

def generate_options_signal(
    index_name: str,
    spot_price: float,
    intraday_df: pd.DataFrame,
    daily_prev_ohlc: dict,
    option_chain: pd.DataFrame
) -> Dict[str, Any]:
    """
    Directional options strategy recommendations (Calls or Puts) based on index momentum.
    Translates index spot support/resistance breaches into option premium targets/SLs.
    """
    if intraday_df.empty:
        return {"decision": "NO TRADE", "reason": "No intraday index data available."}
        
    # Calculate Pivot Points from previous session's OHLC
    pivots = calculate_daily_pivots(
        daily_prev_ohlc['High'],
        daily_prev_ohlc['Low'],
        daily_prev_ohlc['Close']
    )
    
    # Calculate RSI on intraday 5m closed candles
    intraday_df = intraday_df.copy()
    intraday_df['RSI'] = calculate_rsi(intraday_df)
    
    # Detect patterns
    patterns = detect_candlestick_patterns(intraday_df)
    intraday_df = pd.concat([intraday_df, patterns], axis=1)
    
    last_bar = intraday_df.iloc[-1]
    rsi_val = last_bar['RSI']
    
    # Check if spot is near pivot levels (S1, S2, R1, R2 within 0.15% tolerance)
    def is_near(level, spot, tolerance=0.0015):
        return abs(spot - level) / level <= tolerance
        
    near_s1 = is_near(pivots['S1'], spot_price)
    near_s2 = is_near(pivots['S2'], spot_price)
    near_r1 = is_near(pivots['R1'], spot_price)
    near_r2 = is_near(pivots['R2'], spot_price)
    
    bullish_candle = last_bar['Hammer'] | last_bar['BullishEngulfing']
    bearish_candle = last_bar['ShootingStar'] | last_bar['BearishEngulfing']
    
    decision = "NO TRADE"
    reason = "Index trading range is neutral. No high-probability confluences detected."
    contract_type = ""
    target_strike = 0.0
    
    # Call Option Buy Trigger: Support + Bullish Candle + RSI Oversold (< 40)
    if (near_s1 or near_s2 or spot_price < pivots['P']) and bullish_candle and (rsi_val <= 40.0):
        decision = "BUY CALL (CE)"
        reason = f"Confluence: Index spot ({spot_price}) verified support with a bullish pattern and oversold RSI ({round(rsi_val, 2)})."
        contract_type = "CE"
        
    # Put Option Buy Trigger: Resistance + Bearish Candle + RSI Overbought (> 60)
    elif (near_r1 or near_r2 or spot_price > pivots['P']) and bearish_candle and (rsi_val >= 60.0):
        decision = "BUY PUT (PE)"
        reason = f"Confluence: Index spot ({spot_price}) rejected resistance with a bearish pattern and overbought RSI ({round(rsi_val, 2)})."
        contract_type = "PE"
        
    if decision != "NO TRADE":
        # Find ATM option details
        atm_row = option_chain[option_chain['Type'] == 'ATM']
        if not atm_row.empty:
            atm_strike = atm_row.iloc[0]['Strike']
            
            # Use ATM strike for direct recommendation
            target_strike = atm_strike
            
            # Get correct premiums and deltas from option chain
            opt_row = option_chain[option_chain['Strike'] == target_strike].iloc[0]
            
            if contract_type == "CE":
                entry_premium = opt_row['CE_Premium']
                delta = opt_row['CE_Delta']
                # SL: Spot index falling below invalidation support (e.g. S1 or S2)
                invalidation_spot = pivots['S2'] if spot_price > pivots['S1'] else pivots['S3']
                spot_risk = spot_price - invalidation_spot
                premium_sl = max(5.0, entry_premium - (delta * spot_risk))
                
                # Target: next resistance
                target_spot = pivots['R1'] if spot_price < pivots['R1'] else pivots['R2']
                spot_gain = target_spot - spot_price
                premium_target = entry_premium + (delta * spot_gain)
            else:
                entry_premium = opt_row['PE_Premium']
                delta = abs(opt_row['PE_Delta']) # Keep delta positive for math
                # SL: Spot index rising above invalidation resistance (e.g. R1 or R2)
                invalidation_spot = pivots['R2'] if spot_price < pivots['R1'] else pivots['R3']
                spot_risk = invalidation_spot - spot_price
                premium_sl = max(5.0, entry_premium - (delta * spot_risk))
                
                # Target: next support
                target_spot = pivots['S1'] if spot_price > pivots['S1'] else pivots['S2']
                spot_gain = spot_price - target_spot
                premium_target = entry_premium + (delta * spot_gain)
                
            contract_name = f"{index_name.replace(' ', '')} {int(target_strike)} {contract_type}"
            
            return {
                "decision": decision,
                "reason": reason,
                "contract": contract_name,
                "strike": target_strike,
                "entry_premium": round(entry_premium, 2),
                "stop_loss": round(premium_sl, 2),
                "target": round(premium_target, 2),
                "rsi": round(rsi_val, 2),
                "pivots": pivots
            }
            
    return {
        "decision": "NO TRADE",
        "reason": reason,
        "contract": "N/A",
        "strike": 0,
        "entry_premium": 0.0,
        "stop_loss": 0.0,
        "target": 0.0,
        "rsi": round(rsi_val, 2),
        "pivots": pivots
    }

def generate_intraday_blueprint(symbol: str, df: pd.DataFrame, strategy: str = "Momentum Breakout") -> Dict[str, Any]:
    """
    Generates an intraday trade plan (pure equity, leverage).
    Uses tighter stops (e.g., 0.5x to 1x ATR) and ORB/Momentum logic.
    """
    if len(df) < 20:
        return {"decision": "NO TRADE", "reason": "Insufficient intraday data.", "indicators": {}}
        
    df = df.copy()
    close_price = float(df['Close'].iloc[-1])
    
    # Intraday specific indicators
    df['RSI'] = calculate_rsi(df)
    df['ATR'] = calculate_atr(df, period=14)
    macd = calculate_macd(df)
    bb = calculate_bollinger_bands(df)
    mas = calculate_moving_averages(df)
    patterns = detect_candlestick_patterns(df)
    
    df = pd.concat([df, macd, bb, mas, patterns], axis=1)
    
    last_row = df.iloc[-1]
    
    # For intraday, ATR is much smaller, we use 1x ATR for Stop Loss
    atr_val = last_row['ATR'] if not pd.isna(last_row['ATR']) else (close_price * 0.005)
    
    decision = "HOLD"
    reason = "No high-probability intraday setups detected."
    entry_price = round(close_price, 2)
    
    if strategy == "Momentum Breakout":
        ema_crossover = last_row['EMA_9'] > last_row['EMA_21']
        macd_bullish = last_row['Histogram'] > 0 and last_row['MACD'] > last_row['Signal']
        if ema_crossover and macd_bullish and last_row['RSI'] > 55:
            decision = "BUY"
            reason = "Intraday Momentum: EMA 9 > EMA 21 with positive MACD divergence."
            
    elif strategy == "Mean Reversion":
        at_lower_band = close_price <= (last_row['BB_Lower'] * 1.002)
        rsi_oversold = last_row['RSI'] < 30
        reversal_candle = last_row['Hammer'] | last_row['BullishEngulfing']
        if at_lower_band and (rsi_oversold or reversal_candle):
            decision = "BUY"
            reason = "Intraday Reversion: Price rejected at lower Bollinger Band."
            entry_price = round(last_row['BB_Lower'], 2)
            
    elif strategy == "Ichimoku Trend":
        # Simplified for intraday: Price > EMA 50 and RSI > 60
        if close_price > last_row['SMA_50'] and last_row['RSI'] > 60:
            decision = "BUY"
            reason = "Intraday Trend: Strong price action above 50-period moving average."
            
    # Tighter Intraday Risk Parameters
    stop_loss = round(entry_price - atr_val, 2)
    target_price = round(entry_price + (atr_val * 2.0), 2) # 1:2 RR ratio
    
    risk = entry_price - stop_loss
    reward = target_price - entry_price
    risk_reward = round(reward / risk, 2) if risk > 0 else 1.0
    
    return {
        "symbol": symbol.upper(),
        "close_price": round(close_price, 2),
        "decision": decision,
        "reason": reason,
        "entry": entry_price,
        "stop_loss": stop_loss,
        "target": target_price,
        "risk_reward": risk_reward,
        "indicators": {
            "RSI": round(last_row['RSI'], 2),
            "ATR": round(atr_val, 2),
            "MACD": round(last_row.get('MACD', 0), 2),
            "NearestSupport": 0.0,
            "NearestResistance": 0.0
        }
    }