"""Parsers and formatters for Lichess API data."""
from __future__ import generator_stop

import unicodedata
from typing import List

from sopel import formatting  # type: ignore

BLACK = unicodedata.lookup('BLACK MEDIUM SMALL SQUARE')
WHITE = unicodedata.lookup('WHITE MEDIUM SMALL SQUARE')
WINNER = unicodedata.lookup('TROPHY')


def format_game_player(data: dict) -> str:
    """Format a game's player ``data`` dict.

    :return: formatted player's information
    """
    rating = data.get('rating') or '???'
    diff = int(data.get('ratingDiff') or '0')
    user = data.get('user') or {}
    name = user.get('name') or 'unknown'
    title = user.get('title')

    if title:
        name = '%s %s' % (formatting.bold(title), name)

    rating_diff = '+0'
    if diff > 0:
        rating_diff = formatting.color('%+d' % diff, formatting.colors.GREEN)
    elif diff < 0:
        rating_diff = formatting.color('%+d' % diff, formatting.colors.RED)

    return '%s (%s) %s' % (name, rating, rating_diff)


def parse_game_type(data: dict) -> str:
    """Parse and format a game's type."""
    is_rated = data.get('rated')
    speed = data.get('speed')
    variant = data.get('variant')

    game_type = 'unknown'

    if speed:
        game_type = '%s (%s)' % (speed, variant or 'standard')

    if is_rated:
        game_type = 'rated %s' % game_type
    else:
        game_type = 'unrated %s' % game_type

    return game_type


def parse_game_data(data: dict) -> List[str]:
    """Parse and format a game ``data`` dict.

    :return: an ordered list of formatted information for that game data
    """
    # build output
    result: List[str] = []

    # game type (speed & variant)
    result.append(parse_game_type(data))

    # players
    players = data.get('players') or {}
    white = players.get('white') or {}
    black = players.get('black') or {}

    white_username = format_game_player(white)
    black_username = format_game_player(black)

    who_won = data.get('winner')
    white_status = WHITE
    black_status = BLACK

    if who_won == 'white':
        white_status = '%s %s' % (WINNER, white_status)
    elif who_won == 'black':
        black_status = '%s %s' % (black_status, WINNER)

    result.append(
        '%s %s vs %s %s' % (
            white_username,
            white_status,
            black_status,
            black_username,
        )
    )

    # opening
    opening = data.get('opening')
    if opening:
        opening_info = opening.get('name') or '(unknown opening)'
        eco = opening.get('eco') or '(?)'
        opening_info = '%s: %s' % (eco, opening_info)
        result.append(opening_info)

    return result
