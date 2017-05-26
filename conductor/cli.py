from pprint import pprint

import click
from click import echo
from prettytable import PrettyTable
from tabulate import tabulate
from click_spinner import spinner

from .config import get_config
from .feeds import run_price_feeds
from .markets import Markets
from .watchdog import (
    watchdog,
    enable_witness,
    disable_witness,
    is_witness_enabled,
    current_signing_key,
    total_missed,
    get_witness,
)


def heading(title):
    echo('%s:\n' % title + (len(title) + 1) * '-')


def output(data, title=None):
    if title:
        heading(title)

    if type(data) == dict:
        pprint(data)
    else:
        echo(data)

    echo('')


context_settings = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=context_settings)
def conductor():
    """Steem Witness Toolkit."""
    pass


@conductor.command()
def init():
    """Add your witness account."""
    account = click.prompt('What is your witness account name?', type=str)
    witness = get_witness(account)
    if witness:
        # todo save to witness.ini
        echo('Imported a witness %s with its existing settings.' % account)
        output(witness)
    else:
        click.confirm('Witness %s does not exist. Would you like to create it?' % account, abort=True)
        witness_url = click.prompt(
            'What is your witness URL? (ie: https://steemit.com/@%s/witness-announcement)' % account,
            type=str,
        )
        witness_props = dict()
        witness_props['account_creation_fee'] = click.prompt(
            'How much should be account creation fee? (ie: 0.500 STEEM)',
            type=str,
        )
        witness_props['maximum_block_size'] = click.prompt(
            'What should be the maximum block size? (ie: 65536)',
            default=65536,
        )
        witness_props['sbd_interest_rate'] = click.prompt(
            'What should be the SBD interest rate? (ie: 100 for 1%)',
            default=100,
        )

        # tx = update_witness(
        #     witness_name=account,
        #     signing_key='',
        #     witness_url=witness_url,
        #     witness_props=witness_props,
        # )
        # # todo add to config
        # echo('Witness %s created!' % account)
        # output(tx)


@conductor.command()
def tickers():
    """Print Tickers."""
    with spinner():
        m = Markets()
        data = {
            "BTC/USD": round(m.btc_usd(), 2),
            "SBD/USD": round(m.sbd_usd_implied(), 3),
            "STEEM/USD": round(m.steem_usd_implied(), 3),
        }
    echo(tabulate(data.items(), headers=['Symbol', 'Price'], numalign="right", tablefmt='orgtbl'))


@conductor.command()
def feed():
    """Update Price Feeds."""
    run_price_feeds()


@conductor.command()
@click.argument('signing_key')
def enable(signing_key):
    """Enable a witness, or change key."""
    tx = enable_witness(signing_key) or 'This key is already set'
    output(tx)


@conductor.command()
@click.confirmation_option(help='Are you sure you want to stop the witness?')
def disable():
    """Disable a witness."""
    tx = disable_witness() or 'Witness already disabled'
    output(tx)


@conductor.command(name='kill-switch')
@click.option('--disable-after', '-a', default=10)
def kill_switch(disable_after):
    """Monitor for misses w/ disable."""
    watchdog(disable_after)


@conductor.command(name='status')
def status():
    """Print basic witness info."""
    with spinner():
        is_enabled = is_witness_enabled()
        signing_key = current_signing_key()
        misses = total_missed()

        t = PrettyTable(["Enabled", "Misses", "Key"])
        t.align = "l"
        t.add_row([is_enabled, misses, signing_key])

    output(t, 'Status')
    output(get_config(), 'Configuration')
