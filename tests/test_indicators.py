import unittest
import pandas as pd
import numpy as np
from utils.indicators import calculate_rsi, calculate_daily_pivots, calculate_ichimoku

class TestIndicators(unittest.TestCase):
    def setUp(self):
        # Create a mock trend dataframe
        dates = pd.date_range(start="2026-01-01", periods=100, freq="D")
        self.df = pd.DataFrame({
            "Open": np.linspace(100, 200, 100),
            "High": np.linspace(105, 205, 100),
            "Low": np.linspace(95, 195, 100),
            "Close": np.linspace(100, 200, 100),
            "Volume": np.linspace(1000, 2000, 100)
        }, index=dates)

    def test_rsi_bounds(self):
        rsi = calculate_rsi(self.df, period=14)
        self.assertEqual(len(rsi), 100)
        # RSI should be between 0 and 100
        self.assertTrue(all(0 <= val <= 100 for val in rsi))

    def test_pivot_points(self):
        pivots = calculate_daily_pivots(100.0, 80.0, 90.0)
        # Pivot P = (100 + 80 + 90) / 3 = 90
        # S1 = 2*90 - 100 = 80
        # R1 = 2*90 - 80 = 100
        self.assertEqual(pivots['P'], 90.0)
        self.assertEqual(pivots['S1'], 80.0)
        self.assertEqual(pivots['R1'], 100.0)

    def test_ichimoku_output(self):
        ichimoku = calculate_ichimoku(self.df)
        self.assertIn('Tenkan', ichimoku.columns)
        self.assertIn('Kijun', ichimoku.columns)
        self.assertIn('Senkou_A', ichimoku.columns)
        self.assertIn('Senkou_B', ichimoku.columns)
        self.assertEqual(len(ichimoku), 100)

if __name__ == '__main__':
    unittest.main()
