import itertools
import logging
import sys

DATA_PATH = '../data'
CURRENCIES = ['eur', 'gbp', 'aud', 'nzd', 'usd', 'cad', 'chf', 'jpy']
PAIRS = list(itertools.combinations(CURRENCIES, 2))


def enable_logs(level=logging.INFO):
    logging.basicConfig(stream=sys.stdout, level=level, format='%(levelname)s: %(message)s')
