from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from .analysis import build_statistics
from .data import load_draws, write_draws
from .scrape import refresh_dataset
from .tickets import generate_coverage_tickets, generate_random_tickets, ticket_metrics


def _write_stats(output: str = "assets/lotto_stats.json") -> dict:
    stats = build_statistics(load_draws())
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    return stats


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lotto-lab",
        description="Saturday Lotto data, diagnostics and mathematically honest ticket coverage tools.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    scrape = sub.add_parser("scrape", help="Refresh draw data from the public results archive")
    scrape.add_argument("--from-year", type=int, default=date.today().year)
    scrape.add_argument("--to-year", type=int, default=date.today().year)

    sub.add_parser("stats", help="Validate CSV data and rebuild assets/lotto_stats.json")
    sub.add_parser("validate", help="Validate and canonicalize the CSV dataset")

    tickets = sub.add_parser("tickets", help="Generate distinct entries")
    tickets.add_argument("--count", type=int, default=10)
    tickets.add_argument("--mode", choices=("coverage", "random"), default="coverage")
    tickets.add_argument("--seed")
    tickets.add_argument("--json", action="store_true")

    refresh = sub.add_parser("refresh", help="Scrape the current year and rebuild statistics")
    refresh.add_argument("--from-year", type=int, default=date.today().year)
    refresh.add_argument("--to-year", type=int, default=date.today().year)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "scrape":
        before, after = refresh_dataset(from_year=args.from_year, to_year=args.to_year)
        print(f"dataset: {before} -> {after} draws")
        return 0

    if args.command == "stats":
        stats = _write_stats()
        print(f"wrote assets/lotto_stats.json for {stats['dataset']['drawCount']} draws")
        return 0

    if args.command == "validate":
        draws = load_draws()
        write_draws(draws)
        print(f"validated {len(draws)} draws and canonicalized CSV ordering")
        return 0

    if args.command == "tickets":
        generator = generate_coverage_tickets if args.mode == "coverage" else generate_random_tickets
        tickets = generator(args.count, seed=args.seed)
        payload = {"mode": args.mode, "tickets": [list(ticket) for ticket in tickets], "metrics": ticket_metrics(tickets)}
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            for index, ticket in enumerate(tickets, start=1):
                print(f"{index:>2}: " + " ".join(f"{number:02d}" for number in ticket))
            metrics = payload["metrics"]
            print(
                f"coverage: {metrics['uniqueNumbers']} unique numbers, "
                f"max overlap {metrics['maxPairwiseOverlap']}, "
                f"Div 1 chance {metrics['divisionOneProbability']:.10%}"
            )
        return 0

    if args.command == "refresh":
        before, after = refresh_dataset(from_year=args.from_year, to_year=args.to_year)
        stats = _write_stats()
        print(f"dataset: {before} -> {after} draws; stats rebuilt for {stats['dataset']['drawCount']} draws")
        return 0

    return 1
