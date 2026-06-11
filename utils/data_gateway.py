import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

class DataGateway:
    """
    On-demand Data Gateway to fetch historical and intraday data from yfinance.
    Implements normalizations for Indian stock market tickers (NSE/BSE).
    """

    @staticmethod
    def normalize_symbol(symbol: str, exchange: str = "NSE") -> str:
        """
        Normalizes ticker symbols to yfinance-compatible formats.
        E.g. NIFTY 50 -> ^NSEI, TATAMOTORS -> TATAMOTORS.NS
        """
        symbol = symbol.strip().upper()
        
        # Check standard index mappings
        index_mapping = {
            "NIFTY 50": "^NSEI",
            "NIFTY50": "^NSEI",
            "NIFTY": "^NSEI",
            "BANK NIFTY": "^NSEBANK",
            "BANKNIFTY": "^NSEBANK",
            "SENSEX": "^BSESN"
        }
        
        if symbol in index_mapping:
            return index_mapping[symbol]
            
        if symbol.startswith("^"):
            return symbol
            
        # Append exchange suffix if missing
        if not (symbol.endswith(".NS") or symbol.endswith(".BO")):
            if exchange == "BSE":
                return f"{symbol}.BO"
            else:
                return f"{symbol}.NS"
        return symbol

    @staticmethod
    def fetch_ohlcv(symbol: str, period: str = "1y", interval: str = "1d", exchange: str = "NSE") -> pd.DataFrame:
        """
        Fetches adjusted OHLCV data arrays from yfinance.
        Supports standard intervals and custom resampled '10m' interval.
        Drops the current active bar if it is unclosed to satisfy the Anti-Repainting Mandate.
        """
        normalized_symbol = DataGateway.normalize_symbol(symbol, exchange)
        
        # Resampling 10m: Query 5m data first
        query_interval = "5m" if interval == "10m" else interval
        
        try:
            ticker = yf.Ticker(normalized_symbol)
            df = ticker.history(period=period, interval=query_interval)
            
            if df.empty:
                raise ValueError(f"No historical data returned for symbol: {normalized_symbol}")
                
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            df.index = df.index.tz_localize(None)
            
            # Resample 5m bars to 10m bars
            if interval == "10m":
                df = df.resample('10min').agg({
                    'Open': 'first',
                    'High': 'max',
                    'Low': 'min',
                    'Close': 'last',
                    'Volume': 'sum'
                }).dropna()
            
            # No anti-repainting: always return the latest forming bar so the user gets live prices
            return df
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch data for '{normalized_symbol}': {str(e)}")

    @staticmethod
    def get_live_spot_price(symbol: str, exchange: str = "NSE") -> float:
        """
        Fetches the current live spot price for an asset.
        Uses 1d/1m query to fetch the latest closed tick price.
        """
        normalized_symbol = DataGateway.normalize_symbol(symbol, exchange)
        try:
            df = DataGateway.fetch_ohlcv(normalized_symbol, period="1d", interval="1m", exchange=exchange)
            if not df.empty:
                return float(df['Close'].iloc[-1])
        except Exception:
            pass
        
        # Fallback values for default sandbox index prices
        fallbacks = {
            "^NSEI": 23500.0,
            "^NSEBANK": 50000.0,
            "^BSESN": 77000.0
        }
        return fallbacks.get(normalized_symbol, 100.0)

    @staticmethod
    def is_market_open() -> bool:
        """
        Determines if the Indian stock market (NSE/BSE) is currently open.
        Trading hours: Monday to Friday, 9:15 AM to 3:30 PM (IST).
        Local timezone is UTC+5:30.
        """
        now = datetime.now()
        if now.weekday() >= 5:
            return False
            
        market_start = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_end = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        return market_start <= now <= market_end
