import unittest
import tempfile
import unittest.mock as mock
from forex.backtest import Backtest


class TestBackTest(unittest.TestCase):

    def test_prices_parsed_properly(self):
        with tempfile.NamedTemporaryFile(mode='w+t') as tmp_file, \
                mock.patch('forex.config.pairs', return_value=[1, 2, 3]):
            tmp_file.writelines(['date1; 1.0; 2.0; 3.0\n',
                                 'date2; 1.1; 2.1; 3.1\n'])
            tmp_file.flush()

            mock_strategy = mock.Mock()
            backtest = Backtest(tmp_file.name, 100, mock_strategy)
            self.assertEqual(backtest.account.balance, 100)
            backtest.account.auto_close_trades = mock.Mock(return_value={})
            backtest.start()
            self.assertEqual(backtest.account.auto_close_trades.call_count, 2)
            backtest.account.auto_close_trades.assert_has_calls([
                mock.call({1: 1.0, 2: 2.0, 3: 3.0}),
                mock.call({1: 1.1, 2: 2.1, 3: 3.1}),
            ])
            self.assertEqual(mock_strategy.execute.call_count, 2)
            mock_strategy.execute.assert_has_calls([
                mock.call(backtest.account, 'date1', {1: 1.0, 2: 2.0, 3: 3.0}),
                mock.call(backtest.account, 'date2', {1: 1.1, 2: 2.1, 3: 3.1})
            ])

    def test_pairs_prices_mismatch(self):
        expected_msg = r'The number of prices in this entry \(date2\) does not match the number of pairs'
        with tempfile.NamedTemporaryFile(mode='w+t') as tmp_file, \
                mock.patch('forex.config.pairs', return_value=[1, 2]), \
                self.assertRaisesRegex(RuntimeError, expected_msg):
            tmp_file.writelines(['date1; 1; 2\n',
                                 'date2; 1; 2; 3\n'])
            tmp_file.flush()

            Backtest(tmp_file.name, 100, mock.Mock()).start()


if __name__ == '__main__':
    unittest.main()
