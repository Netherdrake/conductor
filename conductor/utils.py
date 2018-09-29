from steem.utils import env_unlocked, parse_time
from steem.wallet import Wallet
from steembase.account import PrivateKey
from steembase.storage import (
    configStorage,
    KeyEncryptionKey,
)
from datetime import datetime as dt


def generate_signing_key():
    """Generate a new random signing key-pair."""
    pk = PrivateKey()
    return pk, pk.pubkey


def unlock_steempy_wallet():
    """ Unlock steempy wallet from cli input. """
    wallet = Wallet()
    if KeyEncryptionKey.config_key in configStorage:
        if not env_unlocked():
            wallet.unlock()
            if wallet.locked():
                print('No Wallet password. Quitting.')
                quit(1)
    else:
        print('steempy wallet does not exist.'
              'Please import your active key before publishing feeds.')
        quit(1)


def head_block_lag(steemd_instance) -> int:
    """ Return age of head block (in seconds)."""
    s = steemd_instance
    head_block = s.get_block_header(s.head_block_number)
    head_block_time = parse_time(head_block['timestamp'])
    return (dt.utcnow() - head_block_time).seconds


def wait_for_healthy_node(steem, seconds=120):
    while head_block_lag(steem) > seconds:
        print("RPC Node %s is unhealthy. Skipping..." % steem.hostname)
        steem.next_node()
