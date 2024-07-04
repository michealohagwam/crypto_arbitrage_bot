import unittest
from bot import calculate_profit, calculate_fees

class TestArbitrage(unittest.TestCase):

    def test_calculate_profit(self):
        binance_price = 50000
        bybit_price = 49900
        quantity = 1
        profit = calculate_profit(binance_price, bybit_price, quantity)
        self.assertGreater(profit, 0)

    def test_calculate_fees(self):
        price = 50000
        fee = calculate_fees(price, 'Binance')
        self.assertEqual(fee, 50)  # 0.1% of 50000 is 50

if __name__ == '__main__':
    unittest.main()
