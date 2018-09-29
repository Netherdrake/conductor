import datetime as dt
import time
import traceback
from typing import List

from steem import Steem
from steem.utils import env_unlocked

from .config import witness, props
from .utils import (
    unlock_steempy_wallet,
    head_block_lag,
    wait_for_healthy_node,
)

steem = Steem(tcp_keepalive=False)
null_key = 'STM1111111111111111111111111111111114T1Anm'


def get_witness(account):
    return steem.get_witness_by_account(account)


def total_missed():
    return get_witness(witness('name'))['total_missed']


def current_signing_key():
    return get_witness(witness('name'))['signing_key']


def witness_set_signing_key(signing_key):
    return steem.commit.witness_update(
        signing_key=signing_key,
        url=witness('url'),
        props=props(),
        account=witness('name'))


def witness_set_props(url, new_props):
    return steem.commit.witness_update(
        signing_key=current_signing_key(),
        url=url,
        props=new_props,
        account=witness('name'))


def witness_create(config: dict):
    """ Create a new witness from config file. """
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


    if not env_unlocked():
        print("Must use env variable for kill-switch.")
        return

    wait_for_healthy_node(steem)
    misses = total_missed()
    miss_history = []
    print("Monitoring the witness, current misses: %s" % misses)
    while True:
        try:
            # enforce we're on a healthy rpc node
            wait_for_healthy_node(steem)

            # detect new misses
            diff = total_missed() - misses
            if diff:
                print("Missed %s new blocks!" % diff)
                for _ in range(diff):
                    miss_history.append(dt.datetime.now())
                misses += diff

            # purge old misses
            miss_history = [x for x in miss_history if
                            x + dt.timedelta(hours=24) > dt.datetime.now()]

            if len(miss_history) >= disable_after:
                if keys:
                    witness_set_signing_key(keys[0])
                    print("Witness %s failed over to key: %s" % (witness('name'), keys[0]))
                    watchdog(disable_after, keys[1:])
                else:
                    disable_witness()
                    print("Witness %s Disabled!" % witness('name'))
                return
        except:
            print(time.ctime())
            print(traceback.format_exc())

        time.sleep(30)
