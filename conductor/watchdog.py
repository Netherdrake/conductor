import datetime as dt
import time
import traceback
from typing import List

from steem import Steem

from .config import witness, props
from .utils import unlock_steempy_wallet

steem = Steem()
null_key = 'STM1111111111111111111111111111111114T1Anm'


def get_witness(account):
    return steem.get_witness_by_account(account)


def total_missed():
    return get_witness(witness('name'))['total_missed']


def current_signing_key():
    return get_witness(witness('name'))['signing_key']


def witness_set_signing_key(signing_key):
    unlock_steempy_wallet()
    return steem.commit.witness_update(
        signing_key=signing_key,
        url=witness('url'),
        props=props(),
        account=witness('name'))


def witness_set_props(url, new_props):
    unlock_steempy_wallet()
    return steem.commit.witness_update(
        signing_key=current_signing_key(),
        url=url,
        props=new_props,
        account=witness('name'))


def witness_create(config: dict):
    """ Create a new witness from config file. """
    unlock_steempy_wallet()
    return steem.commit.witness_update(
        signing_key=null_key,
        url=config['witness']['name'],
        props=config['props'],
        account=config['witness']['name'])


def is_witness_enabled():
    return current_signing_key() != null_key


def enable_witness(signing_key):
    if not is_witness_enabled() or current_signing_key() != signing_key:
        return witness_set_signing_key(signing_key)


def disable_witness():
    if is_witness_enabled():
        return witness_set_signing_key('')


def watchdog(disable_after: int, keys: List[str]):
    if not is_witness_enabled():
        print("Cannot monitor a disabled witness.")
        return

    # unlock the wallet when process starts
    unlock_steempy_wallet()

    misses = total_missed()
    miss_history = []
    print("Monitoring the witness, current misses: %s" % misses)
    while True:
        try:
            # detect new misses
            diff = total_missed() - misses
            if diff:
                print("Missed %s new blocks!" % misses)
                for _ in range(diff):
                    miss_history.append(dt.datetime.now())
                misses += diff

            # purge old misses
            miss_history = [x for x in miss_history if
                            dt.datetime.now() - dt.timedelta(hours=24) < x]

            if len(miss_history) > disable_after:
                if keys:
                    witness_set_signing_key(keys[0])
                    print("Witness %s failed over to key: %s" % (witness('name'), keys[0]))
                    watchdog(disable_after, keys[1:])
                else:
                    disable_witness()
                    print("Witness %s Disabled!" % witness('name'))
                return
        except:
            print(traceback.format_exc())

        time.sleep(30)
