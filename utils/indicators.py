import pandas as pd
import numpy as np

def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculates Relative Strength Index (RSI) using Wilder's smoothing technique.
    Ensures no repainting by operating on the closed series.
    """
    if 'Close' not in df.columns:
        raise ValueError("DataFrame must contain 'Close' column")
    
    close = df['Close']
    delta = close.diff()
    
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    # Wilder's smoothing EMA: alpha = 1 / period
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    
    # Avoid division by zero
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)

def calculate_daily_pivots(high: float, low: float, close: float) -> dict:
    """
    Calculates standard Floor Pivot Points based on previous session's OHLC.
    """
    p = (high + low + close) / 3
    s1 = (2 * p) - high
    r1 = (2 * p) - low
    s2 = p - (high - low)
    r2 = p + (high - low)
    s3 = low - 2 * (high - p)
    r3 = high + 2 * (p - low)
    
    return {
        'P': round(p, 2),
        'S1': round(s1, 2), 'R1': round(r1, 2),
        'S2': round(s2, 2), 'R2': round(r2, 2),
        'S3': round(s3, 2), 'R3': round(r3, 2)
    }

def find_support_resistance_levels(df: pd.DataFrame, window: int = 20, threshold: float = 0.0075) -> tuple[list[float], list[float]]:
    """
    Identifies historical support and resistance zones based on local peaks and troughs
    and groups them into horizontal clusters to reduce noise.
    """
    if len(df) < window * 2:
        return [], []
    
    highs = df['High'].values
    lows = df['Low'].values
    
    supports = []
    resistances = []
    
    for i in range(window, len(df) - window):
        # Local maximum (Resistance)
        if highs[i] == max(highs[i - window : i + window + 1]):
            resistances.append(highs[i])
        # Local minimum (Support)
        if lows[i] == min(lows[i - window : i + window + 1]):
            supports.append(lows[i])
            
    # Helper to cluster levels within a percentage tolerance threshold
    def cluster_levels(levels):
        if not levels:
            return []
        levels = sorted(levels)
        clustered = []
        current_cluster = [levels[0]]
        
        for val in levels[1:]:
            mean_val = np.mean(current_cluster)
            if (val - mean_val) / mean_val <= threshold:
                current_cluster.append(val)
            else:
                clustered.append(round(np.mean(current_cluster), 2))
                current_cluster = [val]
        clustered.append(round(np.mean(current_cluster), 2))
        return sorted(clustered)
        
    return cluster_levels(supports), cluster_levels(resistances)

def calculate_ichimoku(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates Ichimoku Cloud components.
    Note: Senkou Span A and B are shifted 26 periods forward,
    Chikou Span is shifted 26 periods backward.
    """
    high_9 = df['High'].rolling(window=9).max()
    low_9 = df['Low'].rolling(window=9).min()
    tenkan = (high_9 + low_9) / 2
    
    high_26 = df['High'].rolling(window=26).max()
    low_26 = df['Low'].rolling(window=26).min()
    kijun = (high_26 + low_26) / 2
    
    # Leading Span A (plotted 26 periods ahead)
    senkou_a = ((tenkan + kijun) / 2).shift(26)
    
    # Leading Span B (plotted 26 periods ahead)
    high_52 = df['High'].rolling(window=52).max()
    low_52 = df['Low'].rolling(window=52).min()
    senkou_b = ((high_52 + low_52) / 2).shift(26)
    
    # Lagging Span (plotted 26 periods behind)
    chikou = df['Close'].shift(-26)
    
    return pd.DataFrame({
        'Tenkan': tenkan.round(2),
        'Kijun': kijun.round(2),
        'Senkou_A': senkou_a.round(2),
        'Senkou_B': senkou_b.round(2),
        'Chikou': chikou.round(2)
    }, index=df.index)
