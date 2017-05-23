import time
import traceback
from collections import deque

import numpy as np
import pandas as pd
from steem import Steem

from .markets import Markets

settings = {
    "sleep_time_seconds": 10 * 60,
    "minimum_spread_pct": 2.0,
    "sbd_usd_peg": True,
    "use_ema": True,
}


class PriceHistory(object):
    def __init__(self, periods=10):
        self.price_history = deque()
        self.periods = periods

    def add_price(self, price):
        self.price_history.append(price)
        if len(self.price_history) > self.periods * 3:
            self.price_history.popleft()

    def calc_ema(self):
        if len(self.price_history) > 1:
            return pd.ewma(np.array(self.price_history), span=self.periods)[-1]


def get_last_published_price(steem, witness_name):
    my_info = steem.get_witness_by_account(witness_name)
    price = 0
    if float(my_info["sbd_exchange_rate"]["quote"].split()[0]) != 0:
        price = float(my_info["sbd_exchange_rate"]["base"].split()[0]) / float(
            my_info["sbd_exchange_rate"]["quote"].split()[0])
    return price


def refresh_price_feeds(witness_name):
    steem = Steem()
    markets = Markets()
    price_history = PriceHistory()

    print("\n" + time.ctime())
    last_price = get_last_published_price(steem, witness_name)
    print("Published STEEM/USD price is: " + format(last_price, ".3f"))

    current_price = markets.steem_usd_implied()
    quote = "1.000"
    if settings['sbd_usd_peg']:
        quote = round(1 / markets.sbd_usd_implied(), 3)
    print("Implied STEEM/USD price is: %.3f" % current_price)

    # if price diverged for more than our defined %, update the feed
    # use price history to smooth market volatility
    price_history.add_price(current_price)
    ema_price = price_history.calc_ema()
    if settings['use_ema'] and ema_price:
        spread = abs(markets.calc_spread(last_price, ema_price))
    else:
        spread = abs(markets.calc_spread(last_price, current_price / float(quote)))
    print("Spread Between Prices: %.3f%%" % spread)
    if spread > settings['minimum_spread_pct']:
        tx = steem.commit.witness_feed_publish(current_price, quote=quote, account=witness_name)
        # print(tx)
        print("Updated the witness price feed.")

    price_history.add_price(current_price)
    print()
    print('Current Price: %s' % current_price)
    print('EMA(%d): %s' % (price_history.periods, price_history.calc_ema()))


def run_price_feeds(witness_name):
    while True:
        try:
            refresh_price_feeds(witness_name)
            time.sleep(settings['sleep_time_seconds'])
        except KeyboardInterrupt:
            print('Quitting...')
            return
        except:
            print(traceback.format_exc())
            time.sleep(10)


if __name__ == '__main__':
    pass
