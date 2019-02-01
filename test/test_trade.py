import unittest
from forex.trade import Trade


class TestTrade(unittest.TestCase):

    def setUp(self):
        self._trade1 = Trade(('a', 'b'), 1, Trade.TYPE_BUY, 100)
        self._trade2 = Trade(('a', 'b'), 1, Trade.TYPE_SELL, 100)

    def test_trade_type(self):
        self.assertTrue(self._trade1.is_buy)
        self.assertFalse(self._trade1.is_sell)

        self.assertTrue(self._trade2.is_sell)
        self.assertFalse(self._trade2.is_buy)

    def test_take_profit_price(self):
        self._trade1.take_profit_price = 1.1
        self.assertEqual(1.1, self._trade1.take_profit_price)

        with self.assertRaises(ValueError):
            self._trade1.take_profit_price = 0.9

        with self.assertRaises(ValueError):
            self._trade2.take_profit_price = 1.1

    def test_stop_loss_price(self):
        self._trade1.stop_loss_price = 0.9
        self.assertEqual(0.9, self._trade1.stop_loss_price)

        with self.assertRaises(ValueError):
            self._trade1.stop_loss_price = 1.1

        with self.assertRaises(ValueError):
            self._trade2.stop_loss_price = 0.9

    def test_current_value(self):
        self.assertEqual(100, int(self._trade1.current_value(1)))
        self.assertEqual(200, int(self._trade1.current_value(2)))
        self.assertEqual(150, int(self._trade1.current_value(1.5)))
        self.assertEqual(70, int(self._trade1.current_value(0.7)))
        self.assertEqual(50, int(self._trade1.current_value(0.5)))

        self.assertEqual(100, int(self._trade2.current_value(1)))
        self.assertEqual(50, int(self._trade2.current_value(2)))
        self.assertEqual(66, int(self._trade2.current_value(1.5)))
        self.assertEqual(142, int(self._trade2.current_value(0.7)))
        self.assertEqual(200, int(self._trade2.current_value(0.5)))

    def test_str(self):
        trade = Trade(('EUR', 'USD'), 1.2, Trade.TYPE_BUY, 300)
        self.assertEqual('-> BUY (\'EUR\', \'USD\') {price=1.2, take_profit_price=None, stop_loss_price=None}',
                         str(trade))


if __name__ == '__main__':
    unittest.main()
