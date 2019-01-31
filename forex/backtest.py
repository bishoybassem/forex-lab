import os
from forex.config import DATA_PATH, PAIRS
from forex.account import Account


class Backtest:

    def __init__(self, prices_filename, balance, strategy):
        self.prices_filename = prices_filename
        self.account = Account(balance)
        self.strategy = strategy

    @staticmethod
    def parse_entry(entry, length):
        parts = entry.strip().split(';', length - 1)
        timestamp = parts[0]
        values = [0] * (len(parts) - 1)
        for i in range(1, len(parts)):
            values[i - 1] = float(parts[i])
        return timestamp, values

    def start(self):
        with open(os.path.join(DATA_PATH, self.prices_filename)) as file:
            while True:
                current_line = file.readline()
                if not current_line:
                    break

                timestamp, prices = self.__class__.parse_entry(current_line, len(PAIRS) + 1)
                prices_dict = {PAIRS[i]: prices[i] for i in range(len(PAIRS))}

                results = self.account.auto_close_trades(prices_dict)
                for trade_id, outcome in results:
                    print('{} Closed t{} with {}'.format(timestamp, trade_id, outcome))

                self.strategy.execute(self.account, timestamp, prices_dict)

        print('Result: %s' % self.account.net_balance_summary(prices_dict))
