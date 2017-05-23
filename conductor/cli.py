import click
from click import echo
from steem import Steem
from tabulate import tabulate

from .feeds import run_price_feeds
from .killswitch import (
    watchdog,
    enable_witness,
    disable_witness,
)
from .markets import Markets

context_settings = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=context_settings)
def witness():
    """Steem Witness Toolkit."""
    pass


@witness.command()
def init():
    """Add your witness account."""
    echo('hi')

    # see if wallet password is present
    # if not, create wallet
    # ask for witness name
    # if active key not present, set it
    # auto-import blockchain settings. ask user to confirm each one.
    # ask if we should enable the witness (if disabled)


@witness.command()
def tickers():
    """Print Tickers."""
    echo('Loading...\n')
    m = Markets()
    data = {
        "BTC/USD": round(m.btc_usd(), 2),
        "SBD/USD": round(m.sbd_usd_implied(), 3),
        "STEEM/USD": round(m.steem_usd_implied(), 3),
    }
    echo(tabulate(data.items(), headers=['Symbol', 'Price'], numalign="right", tablefmt='orgtbl'))


@witness.command()
def feed():
    """Update Price Feeds."""
    run_price_feeds('furion')


@witness.command()
@click.confirmation_option(help='Are you sure you want to start the witness?')
def enable():
    """Enable a witness."""
    enable_witness()


@witness.command()
@click.confirmation_option(help='Are you sure you want to stop the witness?')
def disable():
    """Disable a witness."""
    disable_witness()


@witness.command(name='kill-switch')
def kill_switch():
    """Monitor for misses w/ disable."""
    enable_witness()
    watchdog()


@witness.command(name='docker-test')
def docker_test():
    """ Test if script works. """
    s = Steem()
    echo(s.get_witness_by_account('furion'))
