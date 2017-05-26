import time
import traceback

from steem import Steem

from .config import witness
from .markets import Markets

settings = {
    "sleep_time_seconds": 10 * 60,
    "minimum_spread_pct": 2.0,
    "sbd_usd_peg": True,
}


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

    print("\n" + time.ctime())
    last_price = get_last_published_price(steem, witness_name)
    print("Last published price is: " + format(last_price, ".3f"))

    quote = "1.000"
    if settings['sbd_usd_peg']:
        quote = round(1 / markets.sbd_usd_implied(), 3)
    current_price = round(markets.steem_usd_implied() / float(quote), 3)
    print('Current price: %s' % current_price)

    spread = abs(markets.calc_spread(last_price, current_price))
    print("Spread between prices: %.3f%%" % spread)
    if spread > settings['minimum_spread_pct']:
        steem.commit.witness_feed_publish(current_price, quote=quote, account=witness_name)
        print("Updated the witness price feed.")


def run_price_feeds():
    while True:
        try:
            refresh_price_feeds(witness('name'))
            time.sleep(settings['sleep_time_seconds'])
        except KeyboardInterrupt:
            print('Quitting...')
            return
        except:
            print(traceback.format_exc())
            time.sleep(10)


if __name__ == '__main__':
    pass
