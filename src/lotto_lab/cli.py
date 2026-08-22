from __future__ import annotations

import argparse
import json
from datetime import UTC, date, datetime
from pathlib import Path

from .analysis import build_statistics
from .benchmark import benchmark_portfolio_distributions, benchmark_probability_objectives
from .crowding import generate_anti_crowding_tickets
from .data import load_draws, write_draws
from .exact_benchmark import benchmark_exact_any_prize_objectives
from .optimizer import generate_exact_local_tickets, optimise_any_prize_exact
from .portfolio import exact_any_prize_probability
from .provenance import build_provenance, write_provenance
from .scrape import refresh_dataset
from .search_benchmark import benchmark_exact_local_search
from .simulation import compare_strategies, walk_forward_backtest
from .tickets import (
    generate_any_prize_bound_tickets,
    generate_coverage_tickets,
    generate_division4_bound_tickets,
    generate_random_tickets,
    ticket_metrics,
)
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


def _probability_mode_tickets(
    mode: str,
    count: int,
    *,
    seed: str | int | None,
    candidates_per_ticket: int,
):
    if mode == "coverage":
        return generate_coverage_tickets(
            count,
            seed=seed,
            candidates_per_ticket=candidates_per_ticket,
        )
    if mode == "any-prize-bound":
        return generate_any_prize_bound_tickets(
            count,
            seed=seed,
            candidates_per_ticket=candidates_per_ticket,
        )
    if mode == "division4-bound":
        return generate_division4_bound_tickets(
            count,
            seed=seed,
            candidates_per_ticket=candidates_per_ticket,
        )
    if mode == "exact-local":
        return generate_exact_local_tickets(
            count,
            seed=seed,
            candidates_per_ticket=candidates_per_ticket,
        )
    if mode == "random":
        return generate_random_tickets(count, seed=seed)
    raise ValueError(f"unsupported probability mode: {mode}")


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
    tickets.add_argument(
        "--mode",
        choices=(
            "coverage",
            "any-prize-bound",
            "division4-bound",
            "exact-local",
            "random",
            "anti-crowding",
        ),
        default="coverage",
    )
    tickets.add_argument("--seed")
    tickets.add_argument("--json", action="store_true")

    exact = sub.add_parser(
        "exact-any-prize",
        help="Compute the exact any-prize probability for a generated portfolio",
    )
    exact.add_argument("--count", type=int, default=10)
    exact.add_argument(
        "--mode",
        choices=("coverage", "any-prize-bound", "division4-bound", "exact-local", "random"),
        default="coverage",
    )
    exact.add_argument("--seed", default="exact-any-prize-v214")
    exact.add_argument("--candidates-per-ticket", type=int, default=320)

    optimise = sub.add_parser(
        "optimize-any-prize",
        help="Improve a Coverage portfolio with exact-DP monotonic local search",
    )
    optimise.add_argument("--count", type=int, default=10)
    optimise.add_argument("--seed", default="exact-local-v214")
    optimise.add_argument("--candidates-per-ticket", type=int, default=320)
    optimise.add_argument("--iterations", type=int, default=3)
    optimise.add_argument("--exact-shortlist", type=int, default=5)
    optimise.add_argument("--exploration-candidates", type=int, default=2)

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

    objectives = sub.add_parser(
        "benchmark-objectives",
        help="Compare subset coverage with certified any-prize and Division-4 bound objectives",
    )
    objectives.add_argument("--count", type=int, default=10)
    objectives.add_argument("--portfolios", type=int, default=24)
    objectives.add_argument("--random-portfolios", type=int, default=96)
    objectives.add_argument("--trials", type=int, default=5000)
    objectives.add_argument("--seed", type=int, default=20260822)
    objectives.add_argument("--candidates-per-ticket", type=int, default=320)
    objectives.add_argument("--bootstrap-resamples", type=int, default=2000)

    exact_objectives = sub.add_parser(
        "benchmark-exact-objectives",
        help="Compare portfolio objectives using exact any-prize union probabilities",
    )
    exact_objectives.add_argument("--count", type=int, default=10)
    exact_objectives.add_argument("--portfolios", type=int, default=12)
    exact_objectives.add_argument("--random-portfolios", type=int, default=48)
    exact_objectives.add_argument("--seed", type=int, default=20260822)
    exact_objectives.add_argument("--candidates-per-ticket", type=int, default=320)
    exact_objectives.add_argument("--bootstrap-resamples", type=int, default=2000)

    local_benchmark = sub.add_parser(
        "benchmark-local-search",
        help="Paired exact benchmark of Coverage vs exact-guided local search",
    )
    local_benchmark.add_argument("--count", type=int, default=10)
    local_benchmark.add_argument("--portfolios", type=int, default=8)
    local_benchmark.add_argument("--seed", type=int, default=20260822)
    local_benchmark.add_argument("--candidates-per-ticket", type=int, default=320)
    local_benchmark.add_argument("--iterations", type=int, default=2)
    local_benchmark.add_argument("--exact-shortlist", type=int, default=4)
    local_benchmark.add_argument("--exploration-candidates", type=int, default=1)
    local_benchmark.add_argument("--bootstrap-resamples", type=int, default=1200)

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
            "any-prize-bound": generate_any_prize_bound_tickets,
            "division4-bound": generate_division4_bound_tickets,
            "exact-local": generate_exact_local_tickets,
            "random": generate_random_tickets,
            "anti-crowding": generate_anti_crowding_tickets,
        }
        generated = generators[args.mode](args.count, seed=args.seed)
        payload = {
            "mode": args.mode,
            "tickets": [list(ticket) for ticket in generated],
            "metrics": ticket_metrics(generated),
        }
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            for index, ticket in enumerate(generated, start=1):
                print(f"{index:>2}: " + " ".join(f"{number:02d}" for number in ticket))
            metrics = payload["metrics"]
            certificates = metrics["probabilityCertificates"]
            any_prize = certificates["anyPrize"]
            division4 = certificates["division4OrBetter"]
            division4_status = (
                "exact/global optimum"
                if division4["globallyOptimalForTicketCount"]
                else "lower bound only"
            )
            print(
                f"unique numbers {metrics['uniqueNumbers']}; max overlap {metrics['maxPairwiseOverlap']}; "
                f"triple efficiency {metrics['tripleCoverage']['efficiency']:.1%}; "
                f"Div 1 chance {metrics['divisionOneProbability']:.10%}"
            )
            print(
                f"any-prize certified lower bound {any_prize['bonferroniLowerBound']:.6%}; "
                f"Div 4+ {division4_status}"
            )
        return 0

    if args.command == "exact-any-prize":
        generated = _probability_mode_tickets(
            args.mode,
            args.count,
            seed=args.seed,
            candidates_per_ticket=args.candidates_per_ticket,
        )
        payload = {
            "mode": args.mode,
            "seed": args.seed,
            "tickets": [list(ticket) for ticket in generated],
            "metrics": ticket_metrics(generated),
            "exactAnyPrize": exact_any_prize_probability(generated),
        }
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "optimize-any-prize":
        baseline = generate_coverage_tickets(
            args.count,
            seed=args.seed,
            candidates_per_ticket=args.candidates_per_ticket,
        )
        result = optimise_any_prize_exact(
            baseline,
            seed=f"{args.seed}:search",
            iterations=args.iterations,
            exact_shortlist=args.exact_shortlist,
            exploration_candidates=args.exploration_candidates,
            preserve_division4_optimality=True,
        )
        result["baselineTickets"] = [list(ticket) for ticket in baseline]
        print(json.dumps(result, indent=2))
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

    if args.command == "benchmark-objectives":
        result = benchmark_probability_objectives(
            args.count,
            portfolios_per_objective=args.portfolios,
            random_portfolios=args.random_portfolios,
            trials=args.trials,
            seed=args.seed,
            candidates_per_ticket=args.candidates_per_ticket,
            bootstrap_resamples=args.bootstrap_resamples,
        )
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "benchmark-exact-objectives":
        result = benchmark_exact_any_prize_objectives(
            args.count,
            portfolios_per_objective=args.portfolios,
            random_portfolios=args.random_portfolios,
            seed=args.seed,
            candidates_per_ticket=args.candidates_per_ticket,
            bootstrap_resamples=args.bootstrap_resamples,
        )
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "benchmark-local-search":
        result = benchmark_exact_local_search(
            args.count,
            portfolios=args.portfolios,
            seed=args.seed,
            candidates_per_ticket=args.candidates_per_ticket,
            iterations=args.iterations,
            exact_shortlist=args.exact_shortlist,
            exploration_candidates=args.exploration_candidates,
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
