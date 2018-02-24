import json

import click
from click import echo
from click_spinner import spinner
from funcy import silent
from prettytable import PrettyTable
from steem.amount import Amount
from tabulate import tabulate

from .config import get_config, new_config, set_config
from .feeds import run_price_feeds
from .markets import Markets
from .utils import generate_signing_key
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
        print(json.dumps(data, indent=4))
    else:
        echo(data)

    echo('')


context_settings = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=context_settings)
@click.pass_context
def conductor(ctx):
    """Steem Witness Toolkit."""
    if ctx.invoked_subcommand not in ['init', 'tickers', 'keygen']:
        ensure_witness_hook()


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
        creation_fee = click.prompt(
            'How much do you want the account creation fee to be (STEEM)?',
            default=c['props']['account_creation_fee'],
        )
        if silent(float)(creation_fee):
            creation_fee = "%s STEEM" % float(creation_fee)
        c['props']['account_creation_fee'] = str(Amount(creation_fee))

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
    creation_fee = click.prompt(
        'How much do you want the account creation fee to be (STEEM)?',
        default=c['props']['account_creation_fee'],
    )
    if silent(float)(creation_fee):
        creation_fee = "%s STEEM" % float(creation_fee)
    c['props']['account_creation_fee'] = str(Amount(creation_fee))

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


@conductor.command(name='keygen')
def keygen():
    """Generate a random signing key-pair."""
    pk, pub = generate_signing_key()
    t = PrettyTable(["Private (install on your witness node)",
                     "Public (publish with 'conductor enable' command)"])
    t.align = "l"
    t.add_row([pk, pub])

    output(t, '')


# Operational Commands
# --------------------
@conductor.command()
@click.option('--sbd-peg/--no-sbd-peg', default=False)
def feed(sbd_peg):
    """Update Price Feeds."""
    run_price_feeds(support_peg=sbd_peg)


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
@click.option('--disable-after', '-n', default=5)
@click.option('--keys', '-k', default=None, multiple=True)
def kill_switch(disable_after, keys):
    """Monitor for misses w/ disable."""
    watchdog(disable_after, keys)


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
    echo(tabulate(
        data.items(),
        headers=['Symbol', 'Price'],
        numalign="right", tablefmt='orgtbl'))


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


def ensure_witness_hook():
    """ Ensure the config file exists. Sync witness props from steem."""
    try:
        c = get_config()
        witness = get_witness(c['witness']['name'])
        c['witness']['url'] = witness['url']
        c['props'] = witness['props']
        set_config(c)
    except FileNotFoundError:
        print("Your witness has not been setup yet. Please run:\n",
              "conductor init")
        quit(1)
