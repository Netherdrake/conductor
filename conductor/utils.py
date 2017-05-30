from steembase.account import PrivateKey


def generate_signing_key():
    """Generate a new random signing key-pair."""
    pk = PrivateKey()
    return pk, pk.pubkey
