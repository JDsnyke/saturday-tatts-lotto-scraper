#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}"
cat <<'EOF'
Saturday Lotto Lab

Commands:
  1) refresh current-year data + rebuild site stats
  2) generate 10 balanced-coverage tickets
  3) validate/canonicalize CSV data
  4) show CLI help
EOF
read -r -p "Choose [1-4]: " choice
case "$choice" in
  1) exec python3 -m lotto_lab refresh ;;
  2) exec python3 -m lotto_lab tickets --count 10 --mode coverage ;;
  3) exec python3 -m lotto_lab validate ;;
  *) exec python3 -m lotto_lab --help ;;
esac
