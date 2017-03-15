import time

from steem import Steem

from .markets import Markets

settings = {
    "sleep_time_seconds": 60,
    "minimum_spread_pct": 1.0,
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
    print("Published STEEM/USD price is: " + format(last_price, ".3f"))

    current_price = markets.steem_usd_implied()
    quote = "1.000"
    if settings['sbd_usd_peg']:
        quote = round(1 / markets.sbd_usd_implied(), 3)
    print("Implied STEEM/USD price is: %.3f" % current_price)

    # if price diverged for more than our defined %, update the feed
    spread = abs(markets.calc_spread(last_price, current_price / float(quote)))
    print("Spread Between Prices: %.3f%%" % spread)
    if spread > settings['minimum_spread_pct']:
        tx = steem.commit.witness_feed_publish(current_price, quote=quote, account=witness_name)
        # print(tx)
        print("Updated the witness price feed.")


def run_price_feeds(witness_name):
    while True:
        refresh_price_feeds(witness_name)
        time.sleep(settings['sleep_time_seconds'])


if __name__ == '__main__':
    pass
