from __future__ import annotations

import argparse
import json

from .game_catalog import GAMES, list_games
from .game_probability import (
    cash3_any_order_probability,
    game_odds_summary,
    keno_all_spot_probability,
    keno_match_distribution,
    odds_from_fraction,
)


def _game_row(slug: str) -> dict:
    summary = game_odds_summary(slug)
    computed = summary["computedTopPrize"]
    exact_any = summary["exactAnyPrize"]
    return {
        "slug": slug,
        "name": summary["name"],
        "operator": summary["operator"],
        "mechanic": summary["mechanic"],
        "jurisdictions": summary["jurisdictions"],
        "schedule": summary["schedule"],
        "computedTopOdds": None if computed is None else computed["odds"],
        "officialTopOdds": summary["official_top_odds"],
        "exactAnyPrizeOdds": None if exact_any is None else exact_any["odds"],
        "officialAnyOdds": summary["official_any_odds"],
    }


def _print_game_table(rows: list[dict]) -> None:
    if not rows:
        print("No games matched the requested filters.")
        return
    headers = ("slug", "operator", "mechanic", "top odds", "any-prize odds")
    rendered = []
    for row in rows:
        top = row["computedTopOdds"] or row["officialTopOdds"]
        any_odds = row["exactAnyPrizeOdds"] or row["officialAnyOdds"]
        rendered.append(
            (
                row["slug"],
                row["operator"],
                row["mechanic"],
                "variable" if top is None else f"1 in {top:,.2f}".replace(".00", ""),
                "variable/unverified" if any_odds is None else f"1 in {any_odds:,.2f}".replace(".00", ""),
            )
        )
    widths = [
        max(len(headers[index]), *(len(str(row[index])) for row in rendered))
        for index in range(len(headers))
    ]
    print("  ".join(headers[index].ljust(widths[index]) for index in range(len(headers))))
    print("  ".join("-" * width for width in widths))
    for row in rendered:
        print("  ".join(str(row[index]).ljust(widths[index]) for index in range(len(headers))))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lotto-lab", description="Australian lottery game catalog and exact odds tools")
    sub = parser.add_subparsers(dest="command", required=True)

    games = sub.add_parser("games", help="List sourced Australian lottery game definitions")
    games.add_argument("--operator")
    games.add_argument("--mechanic")
    games.add_argument("--json", action="store_true")

    odds = sub.add_parser("game-odds", help="Show exact/official odds metadata for one game")
    odds.add_argument("--game", choices=tuple(sorted(GAMES)), required=True)

    keno = sub.add_parser("keno", help="Calculate exact Keno match probabilities for a Spot 1–10 selection")
    keno.add_argument("--spot", type=int, choices=range(1, 11), required=True)

    cash3 = sub.add_parser("cash3", help="Calculate Cash 3 Exact Order and Any Order probabilities")
    cash3.add_argument("--digits", required=True, help="Three digits, e.g. 123 or 223")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "games":
        games = list_games()
        if args.operator:
            term = args.operator.casefold()
            games = [game for game in games if term in game.operator.casefold()]
        if args.mechanic:
            games = [game for game in games if game.mechanic == args.mechanic]
        rows = [_game_row(game.slug) for game in games]
        if args.json:
            print(json.dumps(rows, indent=2))
        else:
            _print_game_table(rows)
        return 0

    if args.command == "game-odds":
        print(json.dumps(game_odds_summary(args.game), indent=2))
        return 0

    if args.command == "keno":
        distribution = keno_match_distribution(args.spot)
        payload = {
            "game": "keno-sa",
            "spot": args.spot,
            "allSpotProbability": float(keno_all_spot_probability(args.spot)),
            "allSpotOdds": odds_from_fraction(keno_all_spot_probability(args.spot)),
            "matchDistribution": [
                {
                    "matches": matches,
                    "probability": float(probability),
                    "odds": odds_from_fraction(probability),
                }
                for matches, probability in sorted(distribution.items())
            ],
        }
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "cash3":
        text = args.digits.strip()
        if len(text) != 3 or not text.isdigit():
            raise SystemExit("--digits must contain exactly three digits, e.g. 123 or 223")
        digits = tuple(int(value) for value in text)
        any_order = cash3_any_order_probability(digits)
        payload = {
            "game": "cash-3",
            "digits": list(digits),
            "exactOrderProbability": 0.001,
            "exactOrderOdds": 1000.0,
            "anyOrderProbability": float(any_order),
            "anyOrderOdds": odds_from_fraction(any_order),
            "distinctOrderings": any_order.numerator,
            "note": "Any Order odds depend on the number of distinct permutations of the chosen digit multiset.",
        }
        print(json.dumps(payload, indent=2))
        return 0

    return 1
