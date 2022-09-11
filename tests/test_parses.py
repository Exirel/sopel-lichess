"""Test ``sopel_lichess.parsers``."""
from __future__ import generator_stop

from sopel import formatting

from sopel_lichess.parsers import (BLACK, WHITE, WINNER, format_game_player,
                                   format_player, parse_game_data,
                                   parse_game_type)

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


MOCK_PLAYER_ACCOUNT = {
    "id": "georges",
    "username": "Georges",
    "online": True,
    "perfs": {},
    "createdAt": 1290415680000,
    "disabled": False,
    "tosViolation": False,
    "profile": {
        "country": "EC",
        "location": "string",
        "bio": "Free bugs!",
        "firstName": "Thibault",
        "lastName": "Duplessis",
        "fideRating": 1500,
        "uscfRating": 1500,
        "ecfRating": 1500,
        "links": "github.com/ornicar\r\ntwitter.com/ornicar"
    },
    "seenAt": 1522636452014,
    "patron": True,
    "playTime": {
        "total": 3296897,
        "tv": 12134
    },
    "language": "en-GB",
    "title": "NM",
    "url": "https://lichess.org/@/georges",
    "playing": "https://lichess.org/yqfLYJ5E/black",
    "nbFollowing": 299,
    "nbFollowers": 2735,
    "completionRate": 97,
    "count": {
        "all": 9265,
        "rated": 7157,
        "ai": 531,
        "draw": 340,
        "drawH": 331,
        "loss": 4480,
        "lossH": 4207,
        "win": 4440,
        "winH": 4378,
        "bookmark": 71,
        "playing": 6,
        "import": 66,
        "me": 0
    },
    "streaming": False,
    "followable": True,
    "following": False,
    "blocking": False,
    "followsYou": False
}


def test_parse_game_type():
    """Test parsing of game type."""
    data = {
        'speed': 'bullet',
        'variant': 'standard',
    }
    result = parse_game_type(data)
    assert result == 'unrated bullet (standard)'


def test_parse_game_type_rated_game():
    """Test parsing of game type for a rated game."""
    data = {
        'rated': True,
        'speed': 'bullet',
        'variant': 'standard',
    }
    result = parse_game_type(data)
    assert result == 'rated bullet (standard)'


def test_parse_game_type_no_info():
    """Test parsing of game type without any data."""
    result = parse_game_type({})
    assert result == 'unrated unknown'


def test_format_game_player():
    """Test formatting of a game player."""
    result = format_game_player(MOCK_PLAYER)
    assert result == ' '.join([
        'gefuehlter_FM',
        '(2721)',
        formatting.color('+7', formatting.colors.GREEN),
    ])


def test_format_game_player_with_mark():
    """Test formatting of a game player."""
    result = format_game_player(MOCK_PLAYER, mark=True)
    assert result == ' '.join([
        formatting.bold('gefuehlter_FM'),
        '(2721)',
        formatting.color('+7', formatting.colors.GREEN),
    ])


def test_format_game_player_title():
    """Test formatting of a game player who has a title."""
    result = format_game_player(MOCK_PLAYER_IM)
    assert result == ' '.join([
        formatting.bold('IM'),
        'LANCELOT_06',
        '(2790)',
        formatting.color('-7', formatting.colors.RED),
    ])


def test_format_game_player_no_info():
    """Test formatting of a game player without any data."""
    result = format_game_player({})
    assert result == 'unknown (???) +0'


def test_parse_game_white_won():
    """Test parsing of game data when white won."""
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


def test_parse_game_white_won_white_marked():
    """Test parsing of game data when white won."""
    white_player = '%s %s %s' % (
        format_game_player(MOCK_PLAYER, mark=True), WINNER, WHITE)
    black_player = '%s %s' % (BLACK, format_game_player(MOCK_PLAYER_IM))

    result = ' | '.join(parse_game_data(MOCK_JSON_GAME, for_player='white'))
    expected = ' | '.join([
        'rated bullet (standard)',
        '%s vs %s' % (white_player, black_player),
        'B10: Caro-Kann Defense: Goldman Variation',
    ])
    assert result == expected


def test_parse_game_white_won_black_marked():
    """Test parsing of game data when white won."""
    white_player = '%s %s %s' % (
        format_game_player(MOCK_PLAYER), WINNER, WHITE)
    black_player = '%s %s' % (
        BLACK, format_game_player(MOCK_PLAYER_IM, mark=True))

    result = ' | '.join(parse_game_data(MOCK_JSON_GAME, for_player='black'))
    expected = ' | '.join([
        'rated bullet (standard)',
        '%s vs %s' % (white_player, black_player),
        'B10: Caro-Kann Defense: Goldman Variation',
    ])
    assert result == expected


def test_parse_game_black_won():
    """Test parsing of game data when black won."""
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


def test_parse_game_black_won_white_marked():
    """Test parsing of game data when black won."""
    data = {}
    data.update(MOCK_JSON_GAME)
    data['winner'] = 'black'

    white_player = '%s %s' % (
        format_game_player(MOCK_PLAYER, mark=True), WHITE)
    black_player = '%s %s %s' % (
        BLACK, WINNER, format_game_player(MOCK_PLAYER_IM))

    print(black_player)

    result = ' | '.join(parse_game_data(data, for_player='white'))
    expected = ' | '.join([
        'rated bullet (standard)',
        '%s vs %s' % (white_player, black_player),
        'B10: Caro-Kann Defense: Goldman Variation',
    ])
    assert result == expected


def test_parse_game_black_won_black_marked():
    """Test parsing of game data when black won."""
    data = {}
    data.update(MOCK_JSON_GAME)
    data['winner'] = 'black'

    white_player = '%s %s' % (
        format_game_player(MOCK_PLAYER), WHITE)
    black_player = '%s %s %s' % (
        BLACK, WINNER, format_game_player(MOCK_PLAYER_IM, mark=True))

    print(black_player)

    result = ' | '.join(parse_game_data(data, for_player='black'))
    expected = ' | '.join([
        'rated bullet (standard)',
        '%s vs %s' % (white_player, black_player),
        'B10: Caro-Kann Defense: Goldman Variation',
    ])
    assert result == expected


def test_parse_game_no_info():
    """Test parsing of game data without any data."""
    white_player = '%s %s' % (format_game_player({}), WHITE)
    black_player = '%s %s' % (BLACK, format_game_player({}))
    result = ' | '.join(parse_game_data({}))
    expected = ' | '.join([
        'unrated unknown',
        '%s vs %s' % (white_player, black_player),
    ])
    assert result == expected


def test_format_player():
    """Test formatting a player data."""
    result = format_player(MOCK_PLAYER_ACCOUNT)

    assert result == ' | '.join([
        '%s %s' % (formatting.bold('NM'), 'Georges'),
        'Played %d rated/%d' % (7157, 9265),
        '%s 4440' % WINNER,
        'Following %d/%d' % (299, 2735),
        'Now playing: https://lichess.org/yqfLYJ5E/black',
    ])


def test_format_player_no_info():
    """Test formatting a player data without any data."""
    result = format_player({})

    assert result == ' | '.join([
        'anonymous',
        'Played 0 rated/0',
        '%s 0' % WINNER,
        'Following 0/0',
    ])
