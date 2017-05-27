from pprint import pprint

import click
from click import echo
from click_spinner import spinner
from prettytable import PrettyTable
from tabulate import tabulate

from .config import get_config, new_config, set_config
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
    witness_create,
    witness_set_props,
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


# Config Commands
# ---------------
@conductor.command()
def init():
    """Add your witness account."""
    account = click.prompt('What is your witness account name?', type=str)
    witness = get_witness(account)
    if witness:
        c = new_config()
        c['witness']['name'] = account
        c['witness']['url'] = witness['url']
        c['props'] = witness['props']
        set_config(c)
        echo('Imported a witness %s from its existing settings.' % account)

    else:
        click.confirm('Witness %s does not exist. Would you like to create it?' % account, abort=True)

        c = new_config()
        c['witness']['name'] = account
        c['witness']['url'] = click.prompt(
            'What should be your witness URL?',
            default=c['witness']['url'],
        )
        c['props']['account_creation_fee'] = click.prompt(
            'How much should be account creation fee?',
            default=c['props']['account_creation_fee'],
        )
        c['props']['maximum_block_size'] = click.prompt(
            'What should be the maximum block size?',
            default=c['props']['maximum_block_size'],
        )
        c['props']['sbd_interest_rate'] = click.prompt(
            'What should be the SBD interest rate?',
            default=c['props']['sbd_interest_rate'],
        )
        set_config(c)
        witness_create(c)
        echo('Witness %s created!' % account)


@conductor.command()
def update():
    """Update witness properties."""
    c = get_config()
    c['witness']['url'] = click.prompt(
        'What should be your witness URL?',
        default=c['witness']['url'],
    )
    c['props']['account_creation_fee'] = click.prompt(
        'How much should be account creation fee?',
        default=c['props']['account_creation_fee'],
    )
    c['props']['maximum_block_size'] = click.prompt(
        'What should be the maximum block size?',
        default=c['props']['maximum_block_size'],
    )
    c['props']['sbd_interest_rate'] = click.prompt(
        'What should be the SBD interest rate?',
        default=c['props']['sbd_interest_rate'],
    )

    # verify
    output(c, '\nConfiguration')
    click.confirm('Do you want to commit the updated values?', abort=True)

    # update
    set_config(c)
    witness_set_props(c['witness']['url'], c['props'])
    output('Witness %s Updated' % c['witness']['name'])


# Operational Commands
# --------------------
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
@click.option('--disable-after', '-n', default=10)
@click.option('--second-key', '-k', default=None)
def kill_switch(disable_after, second_key):
    """Monitor for misses w/ disable."""
    watchdog(disable_after, second_key)


# Status Commands
# ---------------
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
