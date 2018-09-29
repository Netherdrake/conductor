conductor - Steem Witness Toolkit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*conductor* is a user friendly, KISS utility for creating, updating and management of your witness.

Requirements
============
This tool has been tested on Linux, and requires **Python 3.5 or higher**.

On Ubuntu, you also need to install libssl-dev for cryptographic utilities.

.. code-block::

   sudo apt install libffi-dev libssl-dev python3 python3-dev python3-pip


We also need the Python library for Steem.

.. code-block::

   pip3 install -U git+git://github.com/Netherdrake/steem-python


Install
=======

.. code-block::

   pip3 install -U git+https://github.com/Netherdrake/conductor


First Steps
===========
conductor is built on top of ``steem-python``, and leverages it's BIP38 encrypted wallet to store our witness
Active key. This key is required for price feed updates.

To create the wallet, and add our key to it, simply run:

.. code-block::

   steempy addkey

(Optional)
If you wish not to have to type your BIP38 wallet password every time you use conductor,
set the UNLOCK environment variable.

.. code-block::

    export UNLOCK=your-wallet-pw

(Optional)
You may also want to set backup RPC nodes to add resilience to conductor.

.. code-block::

    steempy set nodes https://steemd.steemit.com,https://rpc.steemliberator.com,https://gtg.steem.house:8090,https://steemd.privex.io


Creating or importing your witness
==================================

.. code-block::

   conductor init

*conductor* will ask you for your witness (Steem account) name. If the witness already exists, it will import its current settings
from the blockchain.

Otherwise, it will guide you trough the setup wizard, and create the witness for you.


Updating your witness
=====================
If you wish to change one or more of your witness properties, such as witness url, interest rate, block size, etc., you
can do so using ``conductor update`` command.

.. code-block::

    ~ % conductor update
    What should be your witness URL? [https://steemdb.com/@furion/witness]:
    How much do you want the account creation fee to be (STEEM)? [0.500 STEEM]:
    What should be the maximum block size? [65536]:
    What should be the SBD interest rate? [0]: 10

    Configuration:
    ---------------
    {'props': {'account_creation_fee': '0.500 STEEM',
               'maximum_block_size': 65536,
               'sbd_interest_rate': 10},
     'witness': {'name': 'furion', 'url': 'https://steemdb.com/@furion/witness'}}

    Do you want to commit the updated values? [y/N]: n
    Aborted!
    ~ %

Generating block signing key-pairs
==================================
Each node deployment should have its own signing key, to avoid double-signing.
We can generate new random (``/dev/urandom`` based) key-pairs with a simple command:

.. code-block::

    conductor keygen

Enabling your witness
=====================
Enabling your witness is as simple as setting a public signing key.
This command can also be used for key rotation (for example, if you're falling back to a backup witness node).

**To set a public signing key on your witness run:**

.. code-block::

   conductor enable <PUBLIC_SIGNING_KEY>


Disabling a witness
===================
Sometimes you might want to disable your witness yourself. For example, if you're upgrading
your witness server, and don't want to miss any blocks.

**To disable your witness run:**

.. code-block::

   conductor disable


Kill Switch
===========
Kill Switch is a witness monitoring utility, that tracks block misses. If your witness server bugs out, and stops producing blocks,
this tool will automatically disable your witness to avoid further misses.

As of HF20, you must have exported your unlock password to your env (export UNLOCK='your_pwd') to use the killswitch.

**To run a killswitch, simply run:**

.. code-block::

   conductor kill-switch

Optionally, we can provide number of blocks number of blocks we are allowed to miss before kill-switch disables our witness.
We can achieve this by providing ``-n`` argument, like so: ``conductor kill-switch -n 25``.
By default ``-n`` is 10.


Automatic Failover
==================
We can use the Kill Switch to automatically failover as well. Instead of disabling our witness, the kill-switch
can change our signing key to secondary key (backup node), and then monitor that. If all keys
provided trough `-k` flags miss blocks as well, the witness is finally disabled.

**Example**

.. code-block::

   conductor kill-switch -n 2 -k <BACKUP_NODE_PUBLIC_SIGNING_KEY> -k <BACKUP_NODE_2> ...

See ``conductor kill-switch -h`` for more options.

Price Feeds
===========
Price feeds are a vital component of STEEM ecosystem, as they power SBD->STEEM conversions, as well as rewards estimates.
Witnesses act as an oracle between the blockchain and real-world, by providing honest input on what the implied price of STEEM is.
Furthermore, the prices may contain *bias* to loosely support the SBD stablecoin's peg to USD.

*conductor* ships with ``markets`` module from `SteemData <https://steemdata.com/>`_.
This module interfaces with 3rd party exchanges to fetch VWAP (volume weighted average prices) mean (average of VWAP's from all exchanges) prices.

**Exchanges Used:**
 * Bitstamp, Bitfinex, Kraken, OKCoin  for BTC/USD
 * Poloniex, Bittrex for STEEM/BTC and SBD/BTC


**To run pricefeeds, simply run:**

.. code-block::

   conductor feed


**Peg Support:**
Price feeds support SBD peg signalling. You can explicitly define whether or not you'd like to introduce bias
to your price to support the loose $1 USD == $1 SBD peg. If no option is provided, pegging is **disabled** by default.

.. code-block::

   conductor feed --sbd-peg
   conductor feed --no-sbd-peg

Usage
=====

.. code-block::

    ~ % conductor
    Usage: conductor [OPTIONS] COMMAND [ARGS]...

      Steem Witness Toolkit.

    Options:
      -h, --help  Show this message and exit.

    Commands:
    disable      Disable a witness.
    enable       Enable a witness, or change key.
    feed         Update Price Feeds.
    init         Add your witness account.
    keygen       Generate a random signing key-pair.
    kill-switch  Monitor for misses w/ disable.
    status       Print basic witness info.
    tickers      Print Tickers.
    update       Update witness properties.


There are two additional, read only commands we haven't covered yet. ``status`` and ``tickers``.
They simply print some info for us.

**Status**

.. code-block::

    ~ % conductor status
    Status:
    -------
    +---------+--------+-------------------------------------------------------+
    | Enabled | Misses | Key                                                   |
    +---------+--------+-------------------------------------------------------+
    | True    | 105    | STM7WDG2QpThdkRa3G2PYXM7gH9UksoGm4xqoFBrNet6GH7ToNUYx |
    +---------+--------+-------------------------------------------------------+

    Configuration:
    --------------
    {'props': {'account_creation_fee': '0.500 STEEM',
               'maximum_block_size': 65536,
               'sbd_interest_rate': 0},
     'witness': {'name': 'furion', 'url': 'https://steemdb.com/@furion/witness'}}

    ~ %

**Tickers**

.. code-block::

    ~ % conductor tickers
    | Symbol    |   Price |
    |-----------+---------|
    | BTC/USD   | 2444.31 |
    | SBD/USD   |   1.804 |
    | STEEM/USD |    1.19 |
    ~ %

License
-------
MIT.

Pull requests are welcome.
