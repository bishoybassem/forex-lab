import forex.config as cfg
from forex.account import Account


class Backtest:

    def __init__(self, prices_file, balance, strategy):
        self.prices_file = prices_file
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
        pairs = cfg.pairs()
        with open(self.prices_file) as file:
            while True:
                current_line = file.readline()
                if not current_line:
                    break

                timestamp, prices = self.__class__.parse_entry(current_line, len(pairs) + 1)
                prices_dict = {pairs[i]: prices[i] for i in range(len(pairs))}

                results = self.account.auto_close_trades(prices_dict)
                for trade_id, outcome in results:
                    print('{} Closed t{} with {}'.format(timestamp, trade_id, outcome))

                self.strategy.execute(self.account, timestamp, prices_dict)

        print('Result: %s' % self.account.net_balance_summary(prices_dict))
