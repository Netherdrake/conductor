conductor - Steem Witness Toolkit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*conductor* is a user friendly, KISS utility that will help you manage your STEEM witness.

Install
=======

.. code-block::

   pip install -U git+https://github.com/Netherdrake/conductor


First Steps
===========
First, we need to setup our BIP38 encrypted wallet, and import our witness Active key. This key is required for feed updates.
We store it in an encrypted wallet, so that we don't have to provide the key every time we use *conductor*.

Fortunately, *conductor* comes with a wizard that will guide us trough the process. We invoke it with:

.. code-block::

   conductor init

*conductor* will then let us pick a strong wallet password, and import our witness active key.


Blockchain Properties
=====================
Decisions about certain STEEM blockchain properties are delegated to witnesses. Witnesses can influence these properties
by setting them for their witness, and thus effectively casting a vote.

**Blockchain properties include:**
 * Block Size
 * Account Creation Fee

**To set or update blockchain properties, trigger the wizard:**

.. code-block::

  conductor props


Witness Properties
==================

**Witness properties include:**
 * Witness Thread URL

**To set or update witness properties, trigger the wizard:**

.. code-block::

   conductor props


Price Feeds
===========
Price feeds are a vital component of STEEM ecosystem, as they power SBD->STEEM conversions, as well as rewards estimates.
Witnesses act as an oracle between the blockchain and real-world, by providing honest input on what the implied price of STEEM is.
Furthermore, the prices may contain *bias* to loosely support the SBD stablecoin's peg to USD.

*conductor* ships with ``markets`` module from `SteemData <https://steemdata.com/>`_.
This module interfaces with 3rd party exchanges to fetch VWAP (volume weighted average prices) mean (average of VWAP's from all exchanges) prices.

**Exchanges Used:**
 * Bitstamp, Bitfinex, Kraken, OKCoin, BTC-E for BTC/USD
 * Poloniex, Bittrex for STEEM/BTC and SBD/BTC


**To run pricefeeds, simply run:**

.. code-block::

   conductor feed


Kill Switch
===========
Kill Switch is a witness monitoring utility, that tracks block misses. If your witness server bugs out, and stops producing blocks,
this tool will automatically disable your witness to avoid further misses.

**To run a killswitch, simply run:**

.. code-block::

   conductor killswitch 25

``25`` in this case represents the number of blocks we are allowed to miss in rolling 2 hour period before the killswitch kicks in.


Witness Enable/Disable
======================
Sometimes you might want to disable your witness yourself. For example, if you're upgrading
your witness server, and don't want to miss any blocks.

**To disable your witness run:**

.. code-block::

   conductor disable

**To re-enable your witness run:**

.. code-block::

   conductor enable
