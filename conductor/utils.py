from steem.utils import env_unlocked
from steem.wallet import Wallet
from steembase.account import PrivateKey
from steembase.storage import (
    configStorage,
    MasterPassword,
)


def generate_signing_key():
    """Generate a new random signing key-pair."""
    pk = PrivateKey()
    return pk, pk.pubkey


def unlock_steempy_wallet():
    """ Unlock steempy wallet from cli input. """
    wallet = Wallet()
    if MasterPassword.config_key in configStorage:
        if not env_unlocked() and not Wallet.masterpassword:
            pwd = wallet.getPassword(text='BIP38 Wallet Password: ')
            Wallet.masterpassword = MasterPassword(pwd).decrypted_master
            if wallet.locked():
                print('No Wallet password. Quitting.')
                quit(1)
    else:
        print('steempy wallet does not exist.'
              'Please import your active key before publishing feeds.')
        quit(1)
