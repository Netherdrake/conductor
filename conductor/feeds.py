import time
import traceback

from steem import Steem

from .config import witness
from .markets import Markets
from .utils import unlock_steempy_wallet

steem = Steem()
markets = Markets(cache_timeout=30)
settings = {
    "sleep_time_seconds": 10 * 60,
    "minimum_spread_pct": 2.0,
}


def get_last_published_price(witness_name):
    my_info = steem.get_witness_by_account(witness_name)
    price = 0
    if float(my_info["sbd_exchange_rate"]["quote"].split()[0]) != 0:
        price = float(my_info["sbd_exchange_rate"]["base"].split()[0]) / float(
            my_info["sbd_exchange_rate"]["quote"].split()[0])
    return price


def refresh_price_feeds(witness_name, support_peg=False, bias=0.0):
    print(time.ctime())

    # old prices
    old_adj_price = get_last_published_price(witness_name)
    print("Old Price: " + format(old_adj_price, ".3f"))

    # new prices
    steem_usd = markets.steem_usd_implied()
    sbd_usd = markets.sbd_usd_implied()
    quote = round(1 / sbd_usd, 3) if support_peg else "1.000"
    quote_adj_current_price = round(steem_usd / float(quote), 3)
    print('New Price: %s' % quote_adj_current_price)
    print('\nCurrent STEEM price: %.3f USD' % steem_usd)
    print('Current SBD price: %.3f USD' % sbd_usd)
    print('Quote: %s STEEM' % quote)

    # publish new price is spread widens
    spread = abs(markets.calc_spread(old_adj_price, quote_adj_current_price))
    print("\nSpread between prices: %.3f%%" % spread)
    if spread > settings['minimum_spread_pct']:
        steem.commit.witness_feed_publish(steem_usd, quote=quote, account=witness_name)
        print("Updated the witness price feed.")
    print('\n\n')


def run_price_feeds(**kwargs):
    unlock_steempy_wallet()

    while True:
        try:
            refresh_price_feeds(witness('name'), **kwargs)
            time.sleep(settings['sleep_time_seconds'])
        except KeyboardInterrupt:
            print('Quitting...')
            return
        except:
            print(traceback.format_exc())
            time.sleep(10)


if __name__ == '__main__':
    pass
