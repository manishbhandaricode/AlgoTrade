import pandas as pd
import numpy as np

def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    if 'Close' not in df.columns:
        raise ValueError("DataFrame must contain 'Close' column")
    close = df['Close']
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)

def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    close = df['Close']
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return pd.DataFrame({'MACD': macd_line.round(2), 'Signal': signal_line.round(2), 'Histogram': histogram.round(2)})

def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> pd.DataFrame:
    close = df['Close']
    sma = close.rolling(window=period).mean()
    std = close.rolling(window=period).std()
    upper = sma + (std_dev * std)
    lower = sma - (std_dev * std)
    return pd.DataFrame({'BB_Upper': upper.round(2), 'BB_Middle': sma.round(2), 'BB_Lower': lower.round(2)})

def calculate_moving_averages(df: pd.DataFrame) -> pd.DataFrame:
    close = df['Close']
    return pd.DataFrame({
        'EMA_9': close.ewm(span=9, adjust=False).mean().round(2),
        'EMA_21': close.ewm(span=21, adjust=False).mean().round(2),
        'SMA_50': close.rolling(window=50).mean().round(2),
        'SMA_200': close.rolling(window=200).mean().round(2)
    })

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df['High']
    low = df['Low']
    close = df['Close'].shift(1)
    
    tr1 = high - low
    tr2 = (high - close).abs()
    tr3 = (low - close).abs()
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr.round(2)

def calculate_vwap(df: pd.DataFrame) -> pd.Series:
    # VWAP resets daily, so we group by date
    # df index must be a datetime index
    df = df.copy()
    df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['TPV'] = df['Typical_Price'] * df['Volume']
    
    if hasattr(df.index, 'date'):
        # Daily VWAP calculation for intraday charts
        vwap = df.groupby(df.index.date)['TPV'].cumsum() / df.groupby(df.index.date)['Volume'].cumsum()
    else:
        # Fallback if no datetime index
        vwap = df['TPV'].cumsum() / df['Volume'].cumsum()
        
    return vwap.round(2)

def calculate_daily_pivots(high: float, low: float, close: float) -> dict:
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
    if len(df) < window * 2:
        return [], []
    highs = df['High'].values
    lows = df['Low'].values
    supports = []
    resistances = []
    for i in range(window, len(df) - window):
        if highs[i] == max(highs[i - window : i + window + 1]): resistances.append(highs[i])
        if lows[i] == min(lows[i - window : i + window + 1]): supports.append(lows[i])
    def cluster_levels(levels):
        if not levels: return []
        levels = sorted(levels)
        clustered = []
        current_cluster = [levels[0]]
        for val in levels[1:]:
            mean_val = np.mean(current_cluster)
            if (val - mean_val) / mean_val <= threshold: current_cluster.append(val)
            else:
                clustered.append(round(np.mean(current_cluster), 2))
                current_cluster = [val]
        clustered.append(round(np.mean(current_cluster), 2))
        return sorted(clustered)
    return cluster_levels(supports), cluster_levels(resistances)

def calculate_ichimoku(df: pd.DataFrame) -> pd.DataFrame:
    high_9 = df['High'].rolling(window=9).max()
    low_9 = df['Low'].rolling(window=9).min()
    tenkan = (high_9 + low_9) / 2
    high_26 = df['High'].rolling(window=26).max()
    low_26 = df['Low'].rolling(window=26).min()
    kijun = (high_26 + low_26) / 2
    senkou_a = ((tenkan + kijun) / 2).shift(26)
    high_52 = df['High'].rolling(window=52).max()
    low_52 = df['Low'].rolling(window=52).min()
    senkou_b = ((high_52 + low_52) / 2).shift(26)
    chikou = df['Close'].shift(-26)
    return pd.DataFrame({
        'Tenkan': tenkan.round(2),
        'Kijun': kijun.round(2),
        'Senkou_A': senkou_a.round(2),
        'Senkou_B': senkou_b.round(2),
        'Chikou': chikou.round(2)
    }, index=df.index)
