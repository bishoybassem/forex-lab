import unittest
from forex.trade import Trade
from forex.account import Account


class TestAccount(unittest.TestCase):

    def test_create_trade(self):
        account = Account(100)
        trade_id, trade = account.open_trade(('a', 'b'), 1, Trade.TYPE_BUY, 60, 2, 0.5)
        self.assertEqual(40, account.balance)
        self.assertEqual(1, len(account.trades_list))
        self.assertIn(trade, account.trades_list)
        self.assertEqual(1, trade_id)
        self.assertEqual(('a', 'b'), trade.pair)
        self.assertEqual(1, trade.price)
        self.assertEqual(60, trade.amount)
        self.assertEqual(2, trade.take_profit_price)
        self.assertEqual(0.5, trade.stop_loss_price)

    def test_not_enough_balance(self):
        account = Account(100)
        with self.assertRaises(RuntimeError):
            account.open_trade(('a', 'b'), 1, Trade.TYPE_BUY, 200)
        self.assertEqual(100, account.balance)
        self.assertEqual(0, len(account.trades_list))

    def test_close_trade(self):
        account = Account(100)
        account.open_trade(('a', 'b'), 1, Trade.TYPE_BUY, 60)
        self.assertEqual(40, account.balance)
        self.assertEqual(Account.OUTCOME_LOSS, account.close_trade(1, 0.5))
        self.assertEqual(70, account.balance)
        account.open_trade(('a', 'b'), 2, Trade.TYPE_SELL, 50)
        self.assertEqual(20, account.balance)
        self.assertEqual(Account.OUTCOME_PROFIT, account.close_trade(2, 1))
        self.assertEqual(120, account.balance)

    def test_auto_close_trade(self):
        account = Account(100)
        account.open_trade(('a', 'b'), 1, Trade.TYPE_BUY, 30)
        account.open_trade(('a', 'b'), 1, Trade.TYPE_BUY, 30, 1.25, 0.75)
        account.open_trade(('c', 'd'), 1, Trade.TYPE_SELL, 30, 0.5, 1.5)
        self.assertEqual([], account.auto_close_trades({('a', 'b'): 1, ('c', 'd'): 1}))
        self.assertEqual(3, len(account.trades_list))
        self.assertEqual([], account.auto_close_trades({('a', 'b'): 1.2, ('c', 'd'): 0.7}))
        self.assertEqual(3, len(account.trades_list))
        self.assertEqual([(2, 'profit'), (3, 'loss')], account.auto_close_trades({('a', 'b'): 1.3, ('c', 'd'): 1.75}))
        self.assertEqual(1, len(account.trades_list))

    def test_net_balance_summary(self):
        account = Account(100)
        account.open_trade(('a', 'b'), 1, Trade.TYPE_BUY, 40)
        account.open_trade(('c', 'd'), 1, Trade.TYPE_SELL, 40)
        self.assertEqual('90 units - trades [open [1, 2], 2 total, 0 wins, 0 losses]',
                         account.net_balance_summary({('a', 'b'): 1.25, ('c', 'd'): 2}))
        self.assertEqual('80 units - trades [open [1, 2], 2 total, 0 wins, 0 losses]',
                         account.net_balance_summary({('a', 'b'): 0.5, ('c', 'd'): 1}))
        account.close_trade(2, 4)
        self.assertEqual('70 units - trades [open [1], 2 total, 0 wins, 1 losses]',
                         account.net_balance_summary({('a', 'b'): 1}))
        account.close_trade(1, 1.5)
        self.assertEqual('90 units - trades [open [], 2 total, 1 wins, 1 losses]',
                         account.net_balance_summary({}))


if __name__ == '__main__':
    unittest.main()
