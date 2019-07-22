import logging
import forex.config as cfg
from forex.strategy import AbstractStrategy
from forex.backtest import Backtest
from forex.trade import Trade
import forex.historical as hist


class VerySimpleStrategy(AbstractStrategy):
    """
    A strategy that alternates between the configured currency pairs, always buying with a take profit
    and stop loss percentages.
    """

    def __init__(self, units_per_trade, take_profit_percentage, stop_loss_percentage):
        super().__init__()
        self._units_per_trade = units_per_trade
        self._take_profit_percentage = take_profit_percentage
        self._stop_loss_percentage = stop_loss_percentage
        self._pairs = cfg.pairs()
        self._pair_index = 0

    def execute(self, account, timestamp, current_prices):
        if account.balance >= self._units_per_trade:
            pair = self._pairs[self._pair_index]
            price = current_prices[pair]
            trade_type = Trade.TYPE_BUY
            amount = self._units_per_trade
            take_profit_price = (1 + (self._take_profit_percentage / 100)) * price
            stop_loss_percentage = (1 - (self._stop_loss_percentage / 100)) * price
            trade_id, trade = account.open_trade(pair, price, trade_type, amount,
                                                 take_profit_price, stop_loss_percentage)
            logging.debug('{} Opened t{} with {}'.format(timestamp, trade_id, trade))

        self._pair_index = (self._pair_index + 1) % len(self._pairs)


if __name__ == '__main__':
    cfg.configure_logs(logging.DEBUG)
    prices_file = hist.prepare_data(2018, 2019)
    strategy = VerySimpleStrategy(20, 15, 10)
    Backtest(prices_file, 1000, strategy).start()
