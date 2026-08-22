from __future__ import annotations

import argparse
import json
from datetime import UTC, date, datetime
from pathlib import Path

from .analysis import build_statistics
from .benchmark import benchmark_portfolio_distributions
from .crowding import generate_anti_crowding_tickets
from .data import load_draws, write_draws
from .provenance import build_provenance, write_provenance
from .scrape import refresh_dataset
from .simulation import compare_strategies, walk_forward_backtest
from .tickets import generate_coverage_tickets, generate_random_tickets, ticket_metrics
from .verify import fetch_secondary_html, parse_secondary_results, verify_latest_draws

SECONDARY_REPORT = Path("assets/secondary_verification.json")


def _load_secondary_report() -> dict | None:
    if not SECONDARY_REPORT.exists():
        return None
    try:
        return json.loads(SECONDARY_REPORT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _write_stats(output: str = "assets/lotto_stats.json") -> dict:
    draws = load_draws()
    stats = build_statistics(draws)
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    provenance = build_provenance(draws, secondary_verification=_load_secondary_report())
    write_provenance(provenance)
    return stats


def _write_secondary_report(limit: int) -> dict:
    draws = load_draws()
    rows = parse_secondary_results(fetch_secondary_html())
    report = verify_latest_draws(draws, rows, limit=limit)
    report["verifiedAt"] = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    SECONDARY_REPORT.parent.mkdir(parents=True, exist_ok=True)
    SECONDARY_REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lotto-lab",
        description="Saturday Lotto data, probability, audit and ticket-portfolio tools.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    scrape = sub.add_parser("scrape", help="Refresh draw data from the primary public results archive")
    scrape.add_argument("--from-year", type=int, default=date.today().year)
    scrape.add_argument("--to-year", type=int, default=date.today().year)

    sub.add_parser("stats", help="Validate CSV data and rebuild statistics/provenance assets")
    sub.add_parser("validate", help="Validate and canonicalize the CSV dataset")

    verify = sub.add_parser("verify-secondary", help="Cross-check newest draws against an independent source")
    verify.add_argument("--latest", type=int, default=10)

    tickets = sub.add_parser("tickets", help="Generate distinct entries")
    tickets.add_argument("--count", type=int, default=10)
    tickets.add_argument("--mode", choices=("coverage", "random", "anti-crowding"), default="coverage")
    tickets.add_argument("--seed")
    tickets.add_argument("--json", action="store_true")

    simulate = sub.add_parser("simulate", help="Monte Carlo comparison of coverage vs QuickPick")
    simulate.add_argument("--count", type=int, default=10)
    simulate.add_argument("--trials", type=int, default=50_000)
    simulate.add_argument("--seed", type=int, default=20260822)

    benchmark = sub.add_parser(
        "benchmark",
        help="Multi-seed coverage-vs-QuickPick portfolio distribution benchmark",
    )
    benchmark.add_argument("--count", type=int, default=10)
    benchmark.add_argument("--coverage-portfolios", type=int, default=50)
    benchmark.add_argument("--random-portfolios", type=int, default=200)
    benchmark.add_argument("--trials", type=int, default=5000)
    benchmark.add_argument("--seed", type=int, default=20260822)
    benchmark.add_argument("--candidates-per-ticket", type=int, default=120)
    benchmark.add_argument("--bootstrap-resamples", type=int, default=2000)

    backtest = sub.add_parser("backtest", help="Leakage-free historical portfolio-structure comparison")
    backtest.add_argument("--count", type=int, default=10)
    backtest.add_argument("--steps", type=int, default=120)
    backtest.add_argument("--seed", type=int, default=20260822)

    refresh = sub.add_parser("refresh", help="Scrape, secondary-verify and rebuild statistics")
    refresh.add_argument("--from-year", type=int, default=date.today().year)
    refresh.add_argument("--to-year", type=int, default=date.today().year)
    refresh.add_argument("--verify-latest", type=int, default=10)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "scrape":
        before, after = refresh_dataset(from_year=args.from_year, to_year=args.to_year)
        print(f"dataset: {before} -> {after} draws")
        return 0

    if args.command == "stats":
        stats = _write_stats()
        print(f"wrote stats/provenance for {stats['dataset']['drawCount']} draws")
        return 0

    if args.command == "validate":
        draws = load_draws()
        write_draws(draws)
        print(f"validated {len(draws)} draws and canonicalized CSV ordering")
        return 0

    if args.command == "verify-secondary":
        report = _write_secondary_report(args.latest)
        print(json.dumps(report, indent=2))
        return 0 if report["ok"] else 2

    if args.command == "tickets":
        generators = {
            "coverage": generate_coverage_tickets,
            "random": generate_random_tickets,
            "anti-crowding": generate_anti_crowding_tickets,
        }
        tickets = generators[args.mode](args.count, seed=args.seed)
        payload = {
            "mode": args.mode,
            "tickets": [list(ticket) for ticket in tickets],
            "metrics": ticket_metrics(tickets),
        }
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            for index, ticket in enumerate(tickets, start=1):
                print(f"{index:>2}: " + " ".join(f"{number:02d}" for number in ticket))
            metrics = payload["metrics"]
            print(
                f"unique numbers {metrics['uniqueNumbers']}; max overlap {metrics['maxPairwiseOverlap']}; "
                f"triple efficiency {metrics['tripleCoverage']['efficiency']:.1%}; "
                f"Div 1 chance {metrics['divisionOneProbability']:.10%}"
            )
        return 0

    if args.command == "simulate":
        print(json.dumps(compare_strategies(args.count, trials=args.trials, seed=args.seed), indent=2))
        return 0

    if args.command == "benchmark":
        result = benchmark_portfolio_distributions(
            args.count,
            coverage_portfolios=args.coverage_portfolios,
            random_portfolios=args.random_portfolios,
            trials=args.trials,
            seed=args.seed,
            candidates_per_ticket=args.candidates_per_ticket,
            bootstrap_resamples=args.bootstrap_resamples,
        )
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "backtest":
        result = walk_forward_backtest(
            load_draws(), ticket_count=args.count, max_steps=args.steps, seed=args.seed
        )
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "refresh":
        before, after = refresh_dataset(from_year=args.from_year, to_year=args.to_year)
        report = _write_secondary_report(args.verify_latest)
        if not report["ok"]:
            print("secondary verification failed; refusing to publish refreshed assets")
            return 2
        stats = _write_stats()
        print(
            f"dataset: {before} -> {after} draws; verified {report['verified']} newest draws; "
            f"stats rebuilt for {stats['dataset']['drawCount']} draws"
        )
        return 0

    return 1
