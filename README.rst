=============
sopel-lichess
=============

Lichess plugin for Sopel (Lichess URL handler). This plugin handle URL
from https://lichess.org for:

* games
* players
* TV channels

Install
=======

The preferred way to install this plugin is through ``pip``::

    $ pip install sopel-lichess

Note that you may need to use ``pip3``, depending on your system and your
installation.

Once this is done, you should configure and enable the plugin::

    $ sopel-plugins configure lichess
    $ sopel-plugins enable lichess

And then, restart your bot: this, again, depends on your system and how you run
your bot.

Lichess API Key
===============

This plugin uses the lichess.org API and requires an API key to work. Read
the `lichess's authentication documentation`__ to get your key.

.. __: https://lichess.org/api#section/Authentication

The plugin can be configured with the Sopel configuration wizard::

    $ sopel-plugins configure lichess

Or manually, by editing your configuration and adding this section::

    [lichess]
    api_key = <YOUR API KEY>

Replace ``<YOUR API KEY>`` by your API key (no quote needed).
