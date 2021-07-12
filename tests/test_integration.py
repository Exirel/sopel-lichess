"""Integration tests for the lichess Sopel plugin."""
from __future__ import generator_stop

from unittest import mock

import pytest
from sopel import formatting
from sopel.tests import rawlist

from sopel_lichess.parsers import BLACK, WHITE, WINNER, parse_game_type
from sopel_lichess.plugin import configure

TMP_CONFIG = """
[core]
owner = testnick
nick = TestBot
enable = coretasks, lichess

[lichess]
api_token = TEST_TOKEN_VALUE
"""

MOCK_JSON_GAME = {
    'id': '13YoaUPC',
    'clock': {'increment': 0, 'initial': 60, 'totalTime': 60},
    'createdAt': 1626019314631,
    'lastMoveAt': 1626019413874,
    'moves':
        'e4 c6 Nc3 d5 Qf3 e6 d4 Nf6 e5 Nfd7 Qg3 c5 dxc5 Nc6 Nf3 Nxc5 Be3 Nd7 '
        'O-O-O Qc7 Nxd5 exd5 e6 Qxg3 exd7+ Bxd7 hxg3 Be6 Ng5 O-O-O f4 Be7 '
        'Nxe6 fxe6 Bd3 g6 g4 Bf6 c3 Kd7 g5 Bg7 g3 Kd6 Rh4 Ne7 Rdh1 Nf5 Bxf5 '
        'exf5 Rxh7 b6 Rxh8 Rxh8 Rxh8 Bxh8 Bd4 Bxd4 cxd4 Kc6 Kc2 Kb5 Kc3 a5 '
        'b3 Kc6 a4 b5 Kd3 b4 g4 fxg4 f5 Kd6 f6 Ke6 Ke3 Kf5 f7 Kxg5 f8=Q',
    'opening': {
        'eco': 'B10',
        'name': 'Caro-Kann Defense: Goldman Variation',
        'ply': 5,
    },
    'players': {
        'black': {
            'rating': 2790,
            'ratingDiff': -7,
            'user': {
                'id': 'lancelot_06',
                'name': 'LANCELOT_06',
                'title': 'IM',
            },
        },
        'white': {
            'rating': 2721,
            'ratingDiff': 7,
            'user': {
                'id': 'gefuehlter_fm',
                'name': 'gefuehlter_FM',
            },
        },
    },
    'rated': True,
    'speed': 'bullet',
    'perf': 'bullet',
    'status': 'resign',
    'variant': 'standard',
    'winner': 'white',
}


@pytest.fixture
def tmpconfig(configfactory):
    return configfactory('test.cfg', TMP_CONFIG)


@pytest.fixture
def mockbot(tmpconfig, botfactory):
    return botfactory.preloaded(tmpconfig, preloads=['lichess'])


@pytest.fixture
def irc(mockbot, ircfactory):
    server = ircfactory(mockbot)
    server.bot.backend.clear_message_sent()
    return server


@pytest.fixture
def user(userfactory):
    return userfactory('Exirel')


def test_player_url(irc, user):
    irc.say(
        user,
        '#channel',
        'Check my profile https://lichess.org/@/Master-Chess86 and battle me!',
    )

    assert irc.bot.backend.message_sent == rawlist(
        'PRIVMSG #channel :Player: Master-Chess86',
    )


def test_game_url(irc, user, requests_mock):
    requests_mock.get(
        'https://lichess.org/game/export/abcdefgh',
        json=MOCK_JSON_GAME,
    )

    irc.say(
        user,
        '#channel',
        'Check this game https://lichess.org/abcdefgh I won!',
    )

    white_player = 'gefuehlter_FM (2721) %s %s %s' % (
        formatting.color('+7', formatting.colors.GREEN),
        WINNER,
        WHITE,
    )
    black_player = '%s %s LANCELOT_06 (2790) %s' % (
        BLACK,
        formatting.bold('IM'),
        formatting.color('-7', formatting.colors.RED),
    )
    expected = [
        parse_game_type({
            'speed': 'bullet',
            'variant': 'standard',
            'rated': True,
        }),
        '%s vs %s' % (white_player, black_player),
        'B10: Caro-Kann Defense: Goldman Variation'
    ]

    assert len(irc.bot.backend.message_sent) == 1
    assert irc.bot.backend.message_sent[-1] == rawlist(
        'PRIVMSG #channel :[lichess] %s' % ' | '.join(expected),
    )[-1]


def test_game_url_404(irc, user, requests_mock):
    requests_mock.get(
        'https://lichess.org/game/export/abcdefgh',
        status_code=404,
    )

    irc.say(
        user,
        '#channel',
        'Check this game https://lichess.org/abcdefgh I won!',
    )

    assert not irc.bot.backend.message_sent


def test_tv_channel_url(irc, user):
    irc.say(
        user,
        '#channel',
        'Check this TV https://lichess.org/tv/blitz so cool!',
    )

    assert irc.bot.backend.message_sent == rawlist(
        'PRIVMSG #channel :TV Channel: blitz',
    )


def test_other_urls(irc, user):
    irc.say(
        user,
        '#channel',
        'Check this page https://lichess.org/something from the website!',
    )
    assert not irc.bot.backend.message_sent, 'Game ID length is 8 characters'

    irc.say(
        user,
        '#channel',
        'Check this page https://lichess.org/short from the website!',
    )
    assert not irc.bot.backend.message_sent, 'Game ID length is 8 characters'

    irc.say(
        user,
        '#channel',
        'Check this page https://lichess.org/abcd/fgh from the website!',
    )
    assert not irc.bot.backend.message_sent, 'Game ID do not contain /'


def test_configure(tmpconfig):
    with mock.patch('sopel.config.types.getpass.getpass') as mock_input:
        mock_input.side_effect = ["TEST_API_TOKEN"]
        configure(tmpconfig)

    assert 'lichess' in tmpconfig
    assert hasattr(tmpconfig.lichess, 'api_token')

    assert tmpconfig.lichess.api_token == 'TEST_API_TOKEN'
