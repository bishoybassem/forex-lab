import itertools

DATA_PATH = './data'
CURRENCIES = ['eur', 'gbp', 'aud', 'nzd', 'usd', 'cad', 'chf', 'jpy']
PAIRS = list(itertools.combinations(CURRENCIES, 2))
