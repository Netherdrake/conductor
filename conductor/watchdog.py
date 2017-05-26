import time

from steem import Steem

from .config import witness, props

steem = Steem()
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


def watchdog(disable_after: int):
    if not is_witness_enabled():
        print("Cannot monitor a disabled witness.")
        return
    threshold = total_missed() + disable_after
    while True:
        if total_missed() > threshold:
            disable_witness()

            print("Witness %s Disabled!" % witness('name'))
            return

        time.sleep(60)
