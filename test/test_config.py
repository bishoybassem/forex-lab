import unittest
import unittest.mock as mock
import forex.config as cfg


class TestConfig(unittest.TestCase):

    def test_default_data_path(self):
        with mock.patch('os.getcwd', return_value='/a/b/c/forex-lab/x/y'):
            self.assertEqual('/a/b/c/forex-lab/data', cfg.default_data_path())

        with mock.patch('os.getcwd', return_value='/x/y/z'):
            self.assertEqual('/x/y/z/data', cfg.default_data_path())

    def test_pairs(self):
        with mock.patch('forex.config.CURRENCIES', [1, 2, 3]):
            self.assertEqual([(1, 2), (1, 3), (2, 3)], cfg.pairs())


if __name__ == '__main__':
    unittest.main()
