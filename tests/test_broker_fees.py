import unittest
from utils.backtester import calculate_indian_transaction_costs

class TestBrokerFees(unittest.TestCase):
    def test_delivery_charges(self):
        # Buy at 100, Sell at 110, Qty 1000
        # Buy turnover = 100,000, Sell turnover = 110,000, Total turnover = 210,000
        # Brokerage = 0
        # STT = 0.001 * 100,000 + 0.001 * 110,000 = 100 + 110 = 210
        # Exchange charges = 0.0000322 * 210,000 = 6.76
        # Stamp duty = 0.00015 * 100,000 = 15
        # SEBI fees = 0.000001 * 210,000 = 0.21
        # GST = 18% of (Brokerage + Exchange) = 0.18 * 6.76 = 1.22
        # Total friction = 210 + 6.76 + 15 + 0.21 + 1.22 = 233.19
        costs = calculate_indian_transaction_costs(100.0, 110.0, 1000, "delivery")
        self.assertEqual(costs['brokerage'], 0.0)
        self.assertEqual(costs['stt'], 210.0)
        self.assertAlmostEqual(costs['total_friction'], 233.19, places=1)

    def test_intraday_charges(self):
        # Qty 10
        # Buy at 1000, Sell at 1050
        # Buy turnover = 10,000, Sell turnover = 10,500, Total = 20,500
        # Brokerage = min(20, 0.0003*10,000) + min(20, 0.0003*10,500) = 3.0 + 3.15 = 6.15
        # STT = 0.025% of Sell turnover = 0.00025 * 10,500 = 2.625 (rounded to 2.63)
        costs = calculate_indian_transaction_costs(1000.0, 1050.0, 10, "intraday")
        self.assertEqual(costs['brokerage'], 6.15)
        self.assertEqual(costs['stt'], 2.62)

    def test_options_charges(self):
        # Premium Buy at 100, Sell at 150, Qty 50
        # Buy premium turnover = 5000, Sell premium turnover = 7500, Total = 12,500
        # Brokerage = ₹20 buy + ₹20 sell = ₹40
        # STT = 0.125% of Sell premium = 0.00125 * 7500 = 9.375 (9.38)
        costs = calculate_indian_transaction_costs(100.0, 150.0, 50, "options")
        self.assertEqual(costs['brokerage'], 40.0)
        self.assertEqual(costs['stt'], 9.38)

if __name__ == '__main__':
    unittest.main()
