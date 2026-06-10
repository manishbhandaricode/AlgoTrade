import pandas as pd
import numpy as np
from typing import Dict, Any
from utils.indicators import calculate_rsi, calculate_ichimoku, find_support_resistance_levels, calculate_daily_pivots
from utils.patterns import detect_candlestick_patterns

def generate_swing_blueprint(symbol: str, df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generates a swing trade plan based on 1D/1W closed bars.
    Evaluates Ichimoku Clouds, RSI, and support/resistance zones.
    """
    if len(df) < 52:
        return {
            "decision": "NO TRADE",
            "reason": f"Insufficient data history ({len(df)} bars). Require at least 52 bars.",
            "indicators": {}
        }
    
    # Calculate indicators
    df = df.copy()
    close_price = float(df['Close'].iloc[-1])
    
    df['RSI'] = calculate_rsi(df)
    ichimoku = calculate_ichimoku(df)
    df = pd.concat([df, ichimoku], axis=1)
    
    # Candlestick patterns
    patterns = detect_candlestick_patterns(df)
    df = pd.concat([df, patterns], axis=1)
    
    # S&R Levels
    supports, resistances = find_support_resistance_levels(df, window=15)
    
    # Find nearest support below current price
    valid_supports = [s for s in supports if s < close_price]
    nearest_support = valid_supports[-1] if valid_supports else (close_price * 0.95)
    
    # Find nearest resistance above current price
    valid_resistances = [r for r in resistances if r > close_price]
    nearest_resistance = valid_resistances[0] if valid_resistances else (close_price * 1.05)
    
    # Check trend indicators on last closed bar
    last_row = df.iloc[-1]
    rsi_val = last_row['RSI']
    tenkan = last_row['Tenkan']
    kijun = last_row['Kijun']
    senkou_a = last_row['Senkou_A']
    senkou_b = last_row['Senkou_B']
    
    # Decision Logic
    # 1. Structural trend: Close above Kijun AND Kumo Cloud
    above_cloud = False
    if not pd.isna(senkou_a) and not pd.isna(senkou_b):
        above_cloud = (close_price > senkou_a) and (close_price > senkou_b)
        
    trend_bullish = above_cloud and (close_price > kijun)
    rsi_bullish = rsi_val > 50.0
    
    # Trigger Hammer or Engulfing close to support (within 3% of support)
    at_support = (close_price - nearest_support) / nearest_support <= 0.03
    reversal_candle = last_row['Hammer'] | last_row['BullishEngulfing']
    
    decision = "HOLD"
    reason = "No active buy triggers. Trend is neutral or stock is overextended."
    
    if trend_bullish and rsi_bullish:
        decision = "BUY"
        reason = "Structural bullish trend confirmed by Ichimoku and strong RSI momentum (>50)."
    elif at_support and reversal_candle:
        decision = "BUY"
        reason = "Bullish candlestick reversal pattern confirmed near strong historical support zone."
        
    # Setup trade parameters
    # Entry: upper boundary of nearest support base
    entry_price = round(nearest_support, 2)
    # Stop-Loss: 1.5% below nearest support base
    stop_loss = round(nearest_support * 0.985, 2)
    # Target: Next major resistance zone
    target_price = round(nearest_resistance, 2)
    
    # R:R Ratio
    risk = entry_price - stop_loss
    reward = target_price - entry_price
    risk_reward = round(reward / risk, 2) if risk > 0 else 1.0
    
    # Invalidation check: If target is below entry or risk exceeds reward
    if target_price <= close_price or risk_reward < 1.0:
        decision = "HOLD"
        reason = "Poor risk-to-reward ratio or trade invalidated by overhead resistance limits."
    
    return {
        "symbol": symbol.upper(),
        "close_price": round(close_price, 2),
        "decision": decision,
        "reason": reason,
        "entry": round(close_price, 2) if decision == "BUY" else entry_price,
        "stop_loss": stop_loss,
        "target": target_price,
        "risk_reward": risk_reward,
        "indicators": {
            "RSI": round(rsi_val, 2),
            "Tenkan": tenkan,
            "Kijun": kijun,
            "AboveCloud": above_cloud,
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
