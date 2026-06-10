import pandas as pd
from typing import List, Dict, Any
from utils.data_gateway import DataGateway
from utils.indicators import calculate_rsi, calculate_daily_pivots

def scan_opening_range_breakout(df_15m: pd.DataFrame) -> tuple[bool, str, float, float]:
    """
    Checks for Opening Range Breakout (ORB) on 15m candlestick data.
    Opening range is established by the first 15-minute candle (9:15 AM - 9:30 AM).
    """
    if len(df_15m) < 2:
        return False, "NEUTRAL", 0.0, 0.0
        
    # First candle of the session defines the boundaries
    orb_candle = df_15m.iloc[0]
    orb_high = orb_candle['High']
    orb_low = orb_candle['Low']
    
    # Current closed price
    current_close = df_15m['Close'].iloc[-1]
    
    # Check if we broke above or below the opening range boundaries
    if current_close > orb_high:
        return True, "BULLISH BREAKOUT", orb_high, orb_low
    elif current_close < orb_low:
        return True, "BEARISH BREAKOUT", orb_high, orb_low
        
    return False, "INSIDE RANGE", orb_high, orb_low

def scan_pivot_confluence(df_5m: pd.DataFrame, daily_prev_ohlc: dict) -> tuple[bool, str, float]:
    """
    Checks if price is within 0.1% of daily S1/S2 or R1/R2 pivot levels
    while RSI is overextended (<35 or >65).
    """
    if df_5m.empty:
        return False, "NEUTRAL", 50.0
        
    # Calculate daily pivots from previous session
    pivots = calculate_daily_pivots(
        daily_prev_ohlc['High'],
        daily_prev_ohlc['Low'],
        daily_prev_ohlc['Close']
    )
    
    # Calculate current RSI
    rsi_series = calculate_rsi(df_5m)
    current_rsi = rsi_series.iloc[-1]
    current_close = df_5m['Close'].iloc[-1]
    
    def within_tolerance(level, price, tolerance=0.001):
        return abs(price - level) / level <= tolerance
        
    near_s1 = within_tolerance(pivots['S1'], current_close)
    near_s2 = within_tolerance(pivots['S2'], current_close)
    near_r1 = within_tolerance(pivots['R1'], current_close)
    near_r2 = within_tolerance(pivots['R2'], current_close)
    
    is_confluent = False
    direction = "NEUTRAL"
    
    if (near_s1 or near_s2) and current_rsi <= 35.0:
        is_confluent = True
        direction = "BULLISH REBOUND"
    elif (near_r1 or near_r2) and current_rsi >= 65.0:
        is_confluent = True
        direction = "BEARISH REJECTION"
        
    return is_confluent, direction, current_rsi

def run_intraday_scan(symbol: str, daily_prev_ohlc: dict) -> Dict[str, Any]:
    """
    Runs both ORB and Pivot Confluence scans on a given stock symbol.
    """
    try:
        # Fetch 15m and 5m data for scanning
        df_15m = DataGateway.fetch_ohlcv(symbol, period="5d", interval="15m")
        df_5m = DataGateway.fetch_ohlcv(symbol, period="5d", interval="5m")
        
        if df_15m.empty or df_5m.empty:
            return {"symbol": symbol, "status": "ERROR", "reason": "No intraday data returned"}
            
        current_spot = float(df_5m['Close'].iloc[-1])
        
        # 1. ORB Check
        orb_triggered, orb_event, orb_high, orb_low = scan_opening_range_breakout(df_15m)
        
        # 2. Pivot Check
        pivot_triggered, pivot_event, current_rsi = scan_pivot_confluence(df_5m, daily_prev_ohlc)
        
        # Determine recommendations
        trigger_event = "NO SIGNAL"
        target_price = 0.0
        stop_loss = 0.0
        
        if orb_triggered:
            trigger_event = f"ORB {orb_event}"
            if "BULLISH" in orb_event:
                stop_loss = round(orb_low, 2)
                target_price = round(current_spot * 1.02, 2)  # Target 2% profit
            else:
                stop_loss = round(orb_high, 2)
                target_price = round(current_spot * 0.98, 2)  # Target 2% downside
                
        elif pivot_triggered:
            trigger_event = f"Pivot {pivot_event}"
            if "BULLISH" in pivot_event:
                stop_loss = round(current_spot * 0.99, 2)
                target_price = round(current_spot * 1.02, 2)
            else:
                stop_loss = round(current_spot * 1.01, 2)
                target_price = round(current_spot * 0.98, 2)
                
        return {
            "symbol": symbol,
            "status": "SUCCESS",
            "trigger_event": trigger_event,
            "spot": round(current_spot, 2),
            "target": target_price,
            "stop_loss": stop_loss,
            "rsi": round(current_rsi, 2)
        }
    except Exception as e:
        return {"symbol": symbol, "status": "ERROR", "reason": str(e)}
