"""Lichess plugin."""
from __future__ import generator_stop

import re
import threading

import requests
from sopel import plugin  # type: ignore
from sopel.bot import Sopel, SopelWrapper  # type: ignore
from sopel.config import Config  # type: ignore
from sopel.trigger import Trigger  # type: ignore

from sopel_lichess import config, parsers

BASE_PATTERN = re.escape(r'https://lichess.org/')
MEMORY_KEY = '__sopel_lichess_api__'
LOCK = threading.Lock()


def setup(bot: Sopel) -> None:
    """Set up the plugin with its config section."""
    bot.settings.define_section('lichess', config.LichessSection)
    api_token = bot.settings.lichess.api_token

    if not api_token:
        raise ValueError('Missing required value for lichess.api_token')

    client = requests.Session()
    client.headers.update({
        'Authorization': 'Bearer %s' % api_token,
        'Accept': 'application/json',
    })

    bot.memory[MEMORY_KEY] = client


def shutdown(bot: Sopel) -> None:
    """Tear down the plugin."""
    try:
        del bot.memory[MEMORY_KEY]
    except KeyError:
        pass


def configure(settings: Config) -> None:
    """Configuration wizard handler for the lichess plugin."""
    settings.define_section('lichess', config.LichessSection)
    settings.lichess.configure_setting(
        'api_token',
        'Lichess personnal API token (required)',
    )


@plugin.url(BASE_PATTERN + r'@/(?P<player_id>[^/\s]+)')
def lichess_player(bot: SopelWrapper, trigger: Trigger) -> None:
    """Handle Lichess player's URL."""
    player_id = trigger.group('player_id')
    bot.say('Player: %s' % player_id)


@plugin.url(BASE_PATTERN + r'(?P<game_id>[a-zA-Z0-9]{8})$')
@plugin.output_prefix('[lichess] ')
def lichess_game(bot: SopelWrapper, trigger: Trigger) -> None:
    """Handle Lichess game's URL."""
    game_id = trigger.group('game_id')

    with LOCK:
        response = bot.memory[MEMORY_KEY].get(
            'https://lichess.org/game/export/%s' % game_id)

    if response.status_code == 200:
        data = response.json()
        result = parsers.parse_game_data(data)
        bot.say(' | '.join(result))


@plugin.url(BASE_PATTERN + r'tv/(?P<channel_id>[^/\s]+)$')
def lichess_tv_channel(bot: SopelWrapper, trigger: Trigger) -> None:
    """Handle Lichess TV channel's URL."""
    channel_id = trigger.group('channel_id')
    bot.say('TV Channel: %s' % channel_id)
