import time

from steem import Steem

steem = Steem()

# TODO: load this from config file instead
disable_after = 10  # disable witness after 10 blocks are missed
witness_name = 'furion'
# signing_key = 'STM7WDG2QpThdkRa3G2PYXM7gH9UksoGm4xqoFBrNet6GH7ToNUYx'
witness_url = "https://steemit.com/steemit/@furion/power-down-no-more"
witness_props = {
    "account_creation_fee": "0.500 STEEM",
    "maximum_block_size": 65536,
    "sbd_interest_rate": 15,
}


def total_missed():
    return steem.get_witness_by_account(witness_name)['total_missed']


def current_signing_key():
    return steem.get_witness_by_account(witness_name)['signing_key']


def witness_set_signing_key(signing_key):
    return steem.commit.witness_update(
        signing_key=signing_key,
        url=witness_url,
        props=witness_props,
        account=witness_name)


def is_witness_enabled():
    return current_signing_key() != 'STM1111111111111111111111111111111114T1Anm'


def enable_witness(signing_key):
    if not is_witness_enabled() and current_signing_key() != signing_key:
        return witness_set_signing_key(signing_key)


def disable_witness():
    if is_witness_enabled():
        return witness_set_signing_key('')


def watchdog():
    if not is_witness_enabled():
        print("Cannot monitor a disabled witness.")
        return
    threshold = total_missed() + disable_after
    while True:
        if total_missed() > threshold:
            disable_witness()

            print("Witness %s Disabled!" % witness_name)
            return

        time.sleep(60)
