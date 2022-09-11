"""Test ``sopel_lichess.plugin``."""
from __future__ import generator_stop

import pytest

from sopel_lichess import plugin

BASE_CONFIG = """
[core]
owner = testnick
nick = TestBot
enable = coretasks, lichess
"""

TMP_CONFIG = BASE_CONFIG + """

[lichess]
api_token = TEST_TOKEN_VALUE
"""


@pytest.fixture
def mockbot(configfactory, botfactory):
    """Sopel Bot fixture."""
    return botfactory(configfactory('test.cfg', TMP_CONFIG))


def test_setup(mockbot):
    """Test plugin's setup hook."""
    assert plugin.MEMORY_KEY not in mockbot.memory

    plugin.setup(mockbot)
    assert hasattr(mockbot.settings, 'lichess')
    assert mockbot.settings.lichess.api_token == 'TEST_TOKEN_VALUE'
    assert plugin.MEMORY_KEY in mockbot.memory
    assert mockbot.memory[plugin.MEMORY_KEY] is not None


def test_setup_no_token(configfactory, botfactory):
    """Test plugin's setup hook when no api_token is set."""
    test_settings = configfactory('base.cfg', BASE_CONFIG)
    test_bot = botfactory(test_settings)

    with pytest.raises(ValueError) as error:
        plugin.setup(test_bot)

    assert str(error.value) == 'Missing required value for lichess.api_token'


def test_shutdown(mockbot):
    """Test plugin's shutdown hook."""
    mockbot.memory[plugin.MEMORY_KEY] = 'Something'
    plugin.shutdown(mockbot)
    assert plugin.MEMORY_KEY not in mockbot.memory, (
        'Bot memory must be cleanse.'
    )


def test_shutdown_no_memory(mockbot):
    """Test plugin's shutdown hook doesn't fail with missing memory key."""
    assert plugin.MEMORY_KEY not in mockbot.memory, 'Precondition failed.'
    plugin.shutdown(mockbot)
    assert plugin.MEMORY_KEY not in mockbot.memory, 'Nothing should be added!'
