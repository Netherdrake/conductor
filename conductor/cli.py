import click
from click import echo
from tabulate import tabulate

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
def unlock():
    echo('hi')
    click.prompt('test?')
    if click.confirm('confirm?'):
        echo('confirmed')


@witness.command()
def tickers():
    echo('Loading...\n')
    m = Markets()
    data = {
        "BTC/USD": round(m.btc_usd(), 2),
        "SBD/USD": round(m.sbd_usd_implied(), 3),
        "STEEM/USD": round(m.steem_usd_implied(), 3),
    }
    echo(tabulate(data.items(), headers=['Symbol', 'Price'], numalign="right", tablefmt='orgtbl'))


@witness.command()
@click.confirmation_option(help='Are you sure you want to stop the witness?')
def disable():
    pass

