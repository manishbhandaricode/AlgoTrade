import unittest
import pandas as pd
import numpy as np
from utils.patterns import detect_candlestick_patterns

class TestPatterns(unittest.TestCase):
    def test_hammer_detection(self):
        # Create a single candle hammer: tiny body, very long lower shadow, no upper shadow
        # body = 2, lower_shadow = 6 (>= 2 * body), upper_shadow = 0 (<= 0.1 * range)
        df = pd.DataFrame([{
            "Open": 10.0,
            "High": 10.0,
            "Low": 2.0,
            "Close": 8.0,
            "Volume": 1000
        }])
        patterns = detect_candlestick_patterns(df)
        self.assertTrue(patterns['Hammer'].iloc[0])
        self.assertFalse(patterns['ShootingStar'].iloc[0])

    def test_shooting_star_detection(self):
        # Create a single candle shooting star: tiny body, very long upper shadow, no lower shadow
        # body = 2, upper_shadow = 6 (>= 2 * body), lower_shadow = 0 (<= 0.1 * range)
        df = pd.DataFrame([{
            "Open": 4.0,
            "High": 12.0,
            "Low": 4.0,
            "Close": 6.0,
            "Volume": 1000
        }])
        patterns = detect_candlestick_patterns(df)
        self.assertTrue(patterns['ShootingStar'].iloc[0])
        self.assertFalse(patterns['Hammer'].iloc[0])

    def test_marubozu_detection(self):
        # Body represents 100% of high-low range (Open=Low, Close=High)
        df = pd.DataFrame([{
            "Open": 10.0,
            "High": 20.0,
            "Low": 10.0,
            "Close": 20.0,
            "Volume": 1000
        }])
        patterns = detect_candlestick_patterns(df)
        self.assertTrue(patterns['Marubozu'].iloc[0])

    def test_engulfing_detection(self):
        # Bullish Engulfing: 
        # Bar 1: Bearish (Open=15, Close=10)
        # Bar 2: Bullish (Open=8, Close=17) -> Engulfs Bar 1
        df = pd.DataFrame([
            {"Open": 15.0, "High": 16.0, "Low": 9.0, "Close": 10.0, "Volume": 1000},
            {"Open": 8.0, "High": 18.0, "Low": 7.0, "Close": 17.0, "Volume": 1000}
        ])
        patterns = detect_candlestick_patterns(df)
        self.assertTrue(patterns['BullishEngulfing'].iloc[1])
        self.assertFalse(patterns['BearishEngulfing'].iloc[1])

if __name__ == '__main__':
    unittest.main()
