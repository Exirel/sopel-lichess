"""Lichess plugin."""
from __future__ import generator_stop

import json
import re
import threading
from typing import Optional

import requests
from sopel import plugin  # type: ignore
from sopel.bot import Sopel, SopelWrapper  # type: ignore
from sopel.config import Config  # type: ignore
from sopel.trigger import Trigger  # type: ignore

from sopel_lichess import config, parsers

# pattern
BASE_PATTERN = re.escape(r'https://lichess.org/')
"""Lichess base URL."""
GAME_ID_PATTERN = r'(?P<game_id>[a-zA-Z0-9]{8})'
"""Game ID pattern."""
TRAILING_PATTERN = r'/?(:?\#.*)?$'
"""Trailing pattern: optional trailing slash and anchor."""
FOR_PLAYER_PATTERN = r'/(?P<for_player>white|black)'
"""Game URL with a selected player (white or black)."""

# constants
MEMORY_KEY = '__sopel_lichess_api__'
LOCK = threading.Lock()
OUTPUT_PREFIX = '[lichess] '


def setup(bot: Sopel) -> None:
    """Set up the plugin with its config section."""
    bot.settings.define_section('lichess', config.LichessSection)
    api_token = bot.settings.lichess.api_token

    if not api_token:
        raise ValueError('Missing required value for lichess.api_token')

    client = requests.Session()
    client.headers.update({
        'Authorization': 'Bearer %s' % api_token,
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


@plugin.url(BASE_PATTERN + r'@/(?P<player_id>[^/\s]+)/?')
@plugin.output_prefix(OUTPUT_PREFIX)
def lichess_player(bot: SopelWrapper, trigger: Trigger) -> None:
    """Handle Lichess player's URL."""
    player_id = trigger.group('player_id')

    with LOCK:
        response = bot.memory[MEMORY_KEY].get(
            'https://lichess.org/api/user/%s' % player_id,
            headers={'Accept': 'application/json'})

    if response.status_code == 200:
        data = response.json()
        result = parsers.format_player(data)
        bot.say(result)


@plugin.url(BASE_PATTERN + GAME_ID_PATTERN + TRAILING_PATTERN)
@plugin.url(
    BASE_PATTERN + GAME_ID_PATTERN + FOR_PLAYER_PATTERN + TRAILING_PATTERN)
@plugin.output_prefix(OUTPUT_PREFIX)
def lichess_game(bot: SopelWrapper, trigger: Trigger) -> None:
    """Handle Lichess game's URL."""
    match_data = trigger.groupdict()
    game_id: str = match_data.get('game_id')
    for_player: Optional[str] = match_data.get('for_player')

    with LOCK:
        response = bot.memory[MEMORY_KEY].get(
            'https://lichess.org/game/export/%s' % game_id,
            headers={'Accept': 'application/json'})

    if response.status_code == 200:
        data = response.json()
        result = parsers.parse_game_data(data, for_player=for_player)
        bot.say(' | '.join(result))


@plugin.url(BASE_PATTERN + r'tv/(?P<channel_id>[^/\s]+)/?$')
@plugin.output_prefix(OUTPUT_PREFIX)
def lichess_tv_channel(bot: SopelWrapper, trigger: Trigger) -> None:
    """Handle Lichess TV channel's URL."""
    channel_id = trigger.group('channel_id')

    with LOCK:
        response = bot.memory[MEMORY_KEY].get(
            'https://lichess.org/api/tv/%s' % channel_id,
            params={'nb': 1},
            headers={'Accept': 'application/x-ndjson'})

    if response.status_code == 200:
        raw = [raw for raw in response.text.split('\n') if raw][0]
        data = json.loads(raw)
        result = parsers.parse_game_data(data)
        game_url = 'https://lichess.org/%s' % data.get('id')
        bot.say(' | '.join(result), trailing=' | %s' % game_url)
