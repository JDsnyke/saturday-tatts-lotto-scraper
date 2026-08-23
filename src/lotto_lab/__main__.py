from __future__ import annotations

import sys

from .cli import main as saturday_main
from .game_cli import main as game_main

GAME_COMMANDS = {"games", "game-odds", "game-catalog-json", "keno", "cash3"}

if len(sys.argv) > 1 and sys.argv[1] in GAME_COMMANDS:
    raise SystemExit(game_main(sys.argv[1:]))

raise SystemExit(saturday_main())
