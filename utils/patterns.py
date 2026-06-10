import pandas as pd
import numpy as np

def detect_candlestick_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Programmatically detects candlestick patterns on a pandas DataFrame.
    Returns a DataFrame of booleans for each pattern.
    Ensures non-repainting by performing math strictly on the index.
    """
    if not all(col in df.columns for col in ['Open', 'High', 'Low', 'Close']):
        raise ValueError("DataFrame must contain Open, High, Low, and Close columns")
    
    open_val = df['Open']
    high_val = df['High']
    low_val = df['Low']
    close_val = df['Close']
    
    body = (close_val - open_val).abs()
    real_body_min = np.minimum(open_val, close_val)
    real_body_max = np.maximum(open_val, close_val)
    
    lower_shadow = real_body_min - low_val
    upper_shadow = high_val - real_body_max
    candle_range = high_val - low_val
    
    # Avoid zero division
    safe_range = candle_range.replace(0, 1e-5)
    safe_body = body.replace(0, 1e-5)
    
    # 1. Hammer
    # Lower shadow is at least twice the real body, upper shadow is less than 10% of range
    is_hammer = (lower_shadow >= 2 * body) & (upper_shadow <= 0.1 * candle_range) & (candle_range > 0)
    
    # 2. Shooting Star
    # Upper shadow is at least twice the real body, lower shadow is less than 10% of range
    is_shooting_star = (upper_shadow >= 2 * body) & (lower_shadow <= 0.1 * candle_range) & (candle_range > 0)
    
    # 3. Marubozu
    # Real body represents 95% or more of the entire candle range
    is_marubozu = (body / safe_range >= 0.95) & (candle_range > 0)
    
    # For engulfing patterns we need shifts of 1 period back
    prev_open = open_val.shift(1)
    prev_close = close_val.shift(1)
    
    prev_body_min = np.minimum(prev_open, prev_close)
    prev_body_max = np.maximum(prev_open, prev_close)
    
    # 4. Bullish Engulfing
    # Current bar must be bullish (Close > Open), previous bar must be bearish (Close < Open)
    # Current body must engulf previous body
    is_bullish_engulfing = (close_val > open_val) & (prev_close < prev_open) & \
                           (real_body_min < prev_body_min) & (real_body_max > prev_body_max)
    
    # 5. Bearish Engulfing
    # Current bar must be bearish (Close < Open), previous bar must be bullish (Close > Open)
    # Current body must engulf previous body
    is_bearish_engulfing = (close_val < open_val) & (prev_close > prev_open) & \
                            (real_body_min < prev_body_min) & (real_body_max > prev_body_max)
    
    return pd.DataFrame({
        'Hammer': is_hammer,
        'ShootingStar': is_shooting_star,
        'Marubozu': is_marubozu,
        'BullishEngulfing': is_bullish_engulfing,
        'BearishEngulfing': is_bearish_engulfing
    }, index=df.index)
