import logging
import os
from abc import ABC, abstractmethod
from forex.config import DATA_PATH, PAIRS


class Trade:

    TYPE_BUY = 'BUY'
    TYPE_SELL = 'SELL'

    def __init__(self, pair, price, units, type_):
        self.pair = pair
        self.price = price
        self.units = units
        self.type_ = type_
        self.take_profit_price = None
        self.stop_loss_price = None

    def __str__(self):
        return '-> {} {} {{price={}, take_profit_price={}, stop_loss_price={}}}'\
            .format(self.type_, self.pair, self.price, self.take_profit_price, self.stop_loss_price)


class StrategyBacktest(ABC):

    def __init__(self, prices_filename, balance):
        self.prices_filename = prices_filename
        self.balance = balance
        self.trades = {}
        self.trade_count = 0
        self.trade_wins = 0
        self.trade_losses = 0
        self.current_prices = None

    def get_current_price(self, pair):
        if pair[0] == pair[1]:
            return 1.0
        if pair in PAIRS:
            index = PAIRS.index(pair)
            return self.current_prices[index + 1]
        index = PAIRS.index(pair[::-1])
        return 1.0 / self.current_prices[index + 1]

    def trade_current_value(self, trade):
        price = self.get_current_price(trade.pair)
        percentage_change = (price - trade.price) / trade.price
        sign = 1 if trade.type_ == Trade.TYPE_BUY else -1
        return (1 + (sign * percentage_change)) * trade.units

    def create_trade(self, pair, units, type_, take_profit_pct=None, stop_loss_pct=None):
        self.trade_count += 1
        price = self.get_current_price(pair)
        trade = Trade(pair, price, units, type_)

        if take_profit_pct:
            sign = 1 if type_ == Trade.TYPE_BUY else -1
            trade.take_profit_price = (1 + (sign * take_profit_pct / 100)) * price

        if stop_loss_pct:
            sign = -1 if type_ == Trade.TYPE_BUY else 1
            trade.stop_loss_price = (1 + (sign * stop_loss_pct / 100)) * price

        self.trades[self.trade_count] = trade
        self.balance -= units
        if self.balance < 0:
            raise RuntimeError('Cannot proceed, balance is negative!')
        logging.debug('{} Opened t{} {}'.format(self.current_prices[0], self.trade_count, trade))

    def close_trade(self, trade_id):
        trade = self.trades[trade_id]
        restored_units = self.trade_current_value(trade)
        del self.trades[trade_id]
        self.balance += restored_units
        if restored_units >= trade.units:
            outcome = 'profit'
            self.trade_wins += 1
        else:
            outcome = 'loss'
            self.trade_losses += 1
        logging.debug('{} Closed t{} with {}'.format(self.current_prices[0], trade_id, outcome))

    def auto_close_trades(self):
        for trade_id, trade in self.trades.copy().items():
            price = self.get_current_price(trade.pair)
            close_trade = (trade.type_ == Trade.TYPE_SELL
                           and trade.take_profit_price is not None and price <= trade.take_profit_price)
            close_trade |= (trade.type_ == Trade.TYPE_SELL
                            and trade.stop_loss_price is not None and price >= trade.stop_loss_price)
            close_trade |= (trade.type_ == Trade.TYPE_BUY
                            and trade.take_profit_price is not None and price >= trade.take_profit_price)
            close_trade |= (trade.type_ == Trade.TYPE_BUY
                            and trade.stop_loss_price is not None and price <= trade.stop_loss_price)
            if close_trade:
                self.close_trade(trade_id)

    def net_balance_summary(self):
        net_balance = self.balance
        for trade in self.trades.values():
            net_balance += self.trade_current_value(trade)
        summary = '{} units - trades [open {}, {} total, {} wins, {} losses]'\
            .format(int(net_balance), list(self.trades.keys()), self.trade_count, self.trade_wins, self.trade_losses)
        logging.debug('{} Net {}'.format(self.current_prices[0], summary))
        return summary

    @staticmethod
    def parse_entry(entry):
        parts = entry.strip().split(';')
        for i in range(1, len(parts)):
            parts[i] = float(parts[i])
        return parts

    def start(self):
        with open(os.path.join(DATA_PATH, self.prices_filename)) as file:
            while True:
                current_line = file.readline()
                if not current_line:
                    break
                self.current_prices = self.__class__.parse_entry(current_line)
                self.auto_close_trades()
                self.execute_strategy()

        logging.info('Result: %s' % self.net_balance_summary())

    @abstractmethod
    def execute_strategy(self):
        pass




