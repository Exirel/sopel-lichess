"""Config section for the lichess plugin."""
from __future__ import generator_stop

from sopel.config import types  # type: ignore


class LichessSection(types.StaticSection):
    """Lichess configuration section."""
    api_token = types.SecretAttribute('api_token', default=None)
    """Lichess personnal API token."""
