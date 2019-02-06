import unittest
import unittest.mock as mock
import tempfile
import os
import forex.historical as hist


class TestModuleFunctions(unittest.TestCase):

    def test_pair_string(self):
        self.assertEqual('eurusd', hist.pair_string(('EuR', 'uSD')))

    def test_year_month(self):
        self.assertEqual('2019', hist.year_month(2019))
        self.assertEqual('201901', hist.year_month(2019, 1))
        self.assertEqual('2019/01', hist.year_month(2019, 1, sep='/'))
        self.assertEqual('2019-12', hist.year_month(2019, 12, sep='-'))

    def test_create_data_directory(self):
        with tempfile.TemporaryDirectory() as tmp_dir, mock.patch('forex.config.DATA_PATH', tmp_dir):
            hist.create_data_directory(('ABC', 'XYZ'))
            self.assertTrue(os.path.isdir(os.path.join(tmp_dir, 'abcxyz')))

    def test_get_archive_path(self):
        with mock.patch('forex.config.DATA_PATH', '/xyz'):
            self.assertEqual('/xyz/ab/2019.zip', hist.get_archive_path(('a', 'b'), 2019))
            self.assertEqual('/xyz/ab/201912.zip', hist.get_archive_path(('a', 'b'), 2019, 12))

    def test_get_prices(self):
        with tempfile.TemporaryDirectory() as tmp_dir, mock.patch('forex.config.DATA_PATH', tmp_dir):
            prices = hist.get_prices(('EUR', 'USD'), 2018)
            self.assertEqual(372607, len(prices))
            self.assertEqual('20180101 170000;1.200370;1.201000;1.200370;1.201000;0', prices[0])
            self.assertEqual('20181231 165900;1.146710;1.146710;1.146350;1.146440;0', prices[-1])
            with mock.patch('forex.historical.download_hist_data') as mocked_download_hist_data:
                hist.get_prices(('EUR', 'USD'), 2018)
                self.assertFalse(mocked_download_hist_data.called)

    def test_merge_all_pairs(self):
        prices_pair1 = ['20180101 170000;1;2;3;4;0',
                        '20180105 180000;5;6;7;8;0']
        prices_pair2 = ['20180101 170000;a;b;c;d;0',
                        '20180102 170000;e;f;g;h;0',
                        '20180106 180000;i;j;k;l;0']
        with mock.patch('forex.config.pairs', return_value=[1, 2]), \
             mock.patch('forex.historical.get_prices', side_effect=[prices_pair1, prices_pair2]):

            expected = [
                ['20180101 170000', '4', 'd'],
                ['20180102 170000', None, 'h'],
                ['20180105 180000', '8', None],
                ['20180106 180000', None, 'l']]
            self.assertEqual(expected, hist.merge_all_pairs(2018))

    def test_fill_gaps(self):
        entries = [
            ['a', '1', '2', None],
            ['b', '4', None, '6'],
            ['c', None, '8', '9']
        ]
        hist.fill_gaps(entries)
        expected = [
            ['a', '1', '2', None],
            ['b', '4', '2', '6'],
            ['c', '4', '8', '9']
        ]
        self.assertEqual(expected, entries)


if __name__ == '__main__':
    unittest.main()
