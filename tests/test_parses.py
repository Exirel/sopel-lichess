from __future__ import generator_stop

from sopel import formatting

from sopel_lichess.parsers import (BLACK, WHITE, WINNER, format_game_player,
                                   parse_game_data, parse_game_type)

MOCK_PLAYER_IM = {
    'rating': 2790,
    'ratingDiff': -7,
    'user': {
        'id': 'lancelot_06',
        'name': 'LANCELOT_06',
        'title': 'IM',
    },
}

MOCK_PLAYER = {
    'rating': 2721,
    'ratingDiff': 7,
    'user': {
        'id': 'gefuehlter_fm',
        'name': 'gefuehlter_FM',
    },
}

MOCK_JSON_GAME = {
    'id': '13YoaUPC',
    'createdAt': 1626019314631,
    'lastMoveAt': 1626019413874,
    'opening': {
        'eco': 'B10',
        'name': 'Caro-Kann Defense: Goldman Variation',
        'ply': 5,
    },
    'players': {
        'black': MOCK_PLAYER_IM,
        'white': MOCK_PLAYER,
    },
    'rated': True,
    'speed': 'bullet',
    'perf': 'bullet',
    'variant': 'standard',
    'status': 'resign',
    'winner': 'white',
}


def test_parse_game_type():
    data = {
        'speed': 'bullet',
        'variant': 'standard',
    }
    result = parse_game_type(data)
    assert result == 'unrated bullet (standard)'


def test_parse_game_type_rated_game():
    data = {
        'rated': True,
        'speed': 'bullet',
        'variant': 'standard',
    }
    result = parse_game_type(data)
    assert result == 'rated bullet (standard)'


def test_parse_game_type_no_info():
    result = parse_game_type({})
    assert result == 'unrated unknown'


def test_format_game_player():
    result = format_game_player(MOCK_PLAYER)
    assert result == ' '.join([
        'gefuehlter_FM',
        '(2721)',
        formatting.color('+7', formatting.colors.GREEN),
    ])


def test_format_game_player_title():
    result = format_game_player(MOCK_PLAYER_IM)
    assert result == ' '.join([
        formatting.bold('IM'),
        'LANCELOT_06',
        '(2790)',
        formatting.color('-7', formatting.colors.RED),
    ])


def test_format_game_player_no_info():
    result = format_game_player({})
    assert result == 'unknown (???) +0'


def test_parse_game_white_won():
    white_player = '%s %s %s' % (
        format_game_player(MOCK_PLAYER), WINNER, WHITE)
    black_player = '%s %s' % (BLACK, format_game_player(MOCK_PLAYER_IM))

    result = ' | '.join(parse_game_data(MOCK_JSON_GAME))
    expected = ' | '.join([
        'rated bullet (standard)',
        '%s vs %s' % (white_player, black_player),
        'B10: Caro-Kann Defense: Goldman Variation',
    ])
    assert result == expected


def test_parse_game_black_won():
    data = {}
    data.update(MOCK_JSON_GAME)
    data['winner'] = 'black'

    white_player = '%s %s' % (
        format_game_player(MOCK_PLAYER), WHITE)
    black_player = '%s %s %s' % (
        BLACK, WINNER, format_game_player(MOCK_PLAYER_IM))

    print(black_player)

    result = ' | '.join(parse_game_data(data))
    expected = ' | '.join([
        'rated bullet (standard)',
        '%s vs %s' % (white_player, black_player),
        'B10: Caro-Kann Defense: Goldman Variation',
    ])
    assert result == expected


def test_parse_game_no_info():
    white_player = '%s %s' % (format_game_player({}), WHITE)
    black_player = '%s %s' % (BLACK, format_game_player({}))
    result = ' | '.join(parse_game_data({}))
    expected = ' | '.join([
        'unrated unknown',
        '%s vs %s' % (white_player, black_player),
    ])
    assert result == expected
