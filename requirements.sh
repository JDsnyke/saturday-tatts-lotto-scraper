#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY'
import sys
print(f"Python {sys.version.split()[0]}")
try:
    import bs4
except ImportError as exc:
    raise SystemExit("Missing dependency: run `python3 -m pip install -r requirements.txt`") from exc
print(f"beautifulsoup4 {bs4.__version__}")
print("Requirements OK")
PY
