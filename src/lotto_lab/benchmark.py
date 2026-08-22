from __future__ import annotations

import random
from collections.abc import Sequence
from statistics import fmean, pstdev

from .domain import BALL_COUNT, MAIN_COUNT
from .tickets import (
    Ticket,
    generate_any_prize_bound_tickets,
    generate_coverage_tickets,
    generate_division4_bound_tickets,
    generate_random_tickets,
    ticket_metrics,
)

MetricRow = dict[str, float]


def _quantile(values: Sequence[float], probability: float) -> float:
    if not values:
        raise ValueError("at least one value is required")
    if not 0 <= probability <= 1:
        raise ValueError("probability must be between 0 and 1")
    ordered = sorted(float(value) for value in values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def distribution_summary(values: Sequence[float]) -> dict[str, float | int]:
    if not values:
        raise ValueError("at least one value is required")
    numeric = [float(value) for value in values]
    return {
        "count": len(numeric),
        "mean": fmean(numeric),
        "stdev": pstdev(numeric),
        "min": min(numeric),
        "p05": _quantile(numeric, 0.05),
        "p25": _quantile(numeric, 0.25),
        "median": _quantile(numeric, 0.50),
        "p75": _quantile(numeric, 0.75),
        "p95": _quantile(numeric, 0.95),
        "max": max(numeric),
    }


def probability_of_superiority(
    coverage_values: Sequence[float],
    random_values: Sequence[float],
    *,
    direction: str = "higher",
) -> float:
    if direction not in {"higher", "lower"}:
        raise ValueError("direction must be 'higher' or 'lower'")
    if not coverage_values or not random_values:
        raise ValueError("both distributions require at least one value")
    wins = 0.0
    total = len(coverage_values) * len(random_values)
    for coverage in coverage_values:
        for baseline in random_values:
            if coverage == baseline:
                wins += 0.5
            elif (coverage > baseline and direction == "higher") or (
                coverage < baseline and direction == "lower"
            ):
                wins += 1.0
    return wins / total


def bootstrap_mean_difference(
    coverage_values: Sequence[float],
    random_values: Sequence[float],
    *,
    direction: str = "higher",
    resamples: int = 2000,
    seed: int = 20260822,
) -> tuple[float, float]:
    if direction not in {"higher", "lower"}:
        raise ValueError("direction must be 'higher' or 'lower'")
    if not coverage_values or not random_values:
        raise ValueError("both distributions require at least one value")
    if resamples < 100:
        raise ValueError("resamples must be at least 100")
    rng = random.Random(seed)
    coverage = [float(value) for value in coverage_values]
    baseline = [float(value) for value in random_values]
    differences = []
    for _ in range(resamples):
        coverage_mean = fmean(rng.choice(coverage) for _ in coverage)
        random_mean = fmean(rng.choice(baseline) for _ in baseline)
        raw = coverage_mean - random_mean
        differences.append(raw if direction == "higher" else -raw)
    return _quantile(differences, 0.025), _quantile(differences, 0.975)


def _sample_main_draws(trials: int, *, seed: int) -> list[frozenset[int]]:
    if trials < 1:
        raise ValueError("trials must be positive")
    rng = random.Random(seed)
    population = list(range(1, BALL_COUNT + 1))
    return [frozenset(rng.sample(population, MAIN_COUNT)) for _ in range(trials)]


def _outcome_rates(tickets: Sequence[Ticket], draws: Sequence[frozenset[int]]) -> dict[str, float]:
    ticket_sets = [frozenset(ticket) for ticket in tickets]
    at_least_three = 0
    at_least_four = 0
    best_match_total = 0
    for draw in draws:
        best = max(len(ticket & draw) for ticket in ticket_sets)
        best_match_total += best
        at_least_three += best >= 3
        at_least_four += best >= 4
    count = len(draws)
    return {
        "anyPrizeRate": at_least_three / count,
        "division4OrBetterRate": at_least_four / count,
        "meanBestMainMatch": best_match_total / count,
    }


def _portfolio_row(tickets: Sequence[Ticket], draws: Sequence[frozenset[int]]) -> MetricRow:
    metrics = ticket_metrics(tickets)
    outcomes = _outcome_rates(tickets, draws)
    certificates = metrics["probabilityCertificates"]
    any_prize = certificates["anyPrize"]
    division4 = certificates["division4OrBetter"]
    division4_certified = division4["exactProbability"]
    if division4_certified is None:
        division4_certified = division4["bonferroniLowerBound"]
    return {
        "pairCoverageEfficiency": float(metrics["pairCoverage"]["efficiency"]),
        "tripleCoverageEfficiency": float(metrics["tripleCoverage"]["efficiency"]),
        "quadCoverageEfficiency": float(metrics["quadrupleCoverage"]["efficiency"]),
        "maxPairwiseOverlap": float(metrics["maxPairwiseOverlap"]),
        "uniqueNumbers": float(metrics["uniqueNumbers"]),
        "anyPrizeBonferroniLowerBound": float(any_prize["bonferroniLowerBound"]),
        "division4CertifiedProbability": float(division4_certified),
        "division4GloballyOptimal": float(bool(division4["globallyOptimalForTicketCount"])),
        **outcomes,
    }


def _comparison(
    coverage_values: Sequence[float],
    random_values: Sequence[float],
    *,
    direction: str,
    resamples: int,
    seed: int,
) -> dict:
    coverage_mean = fmean(coverage_values)
    random_mean = fmean(random_values)
    raw_difference = coverage_mean - random_mean
    favourable_difference = raw_difference if direction == "higher" else -raw_difference
    ci_low, ci_high = bootstrap_mean_difference(
        coverage_values,
        random_values,
        direction=direction,
        resamples=resamples,
        seed=seed,
    )
    return {
        "direction": direction,
        "rawMeanDifference": raw_difference,
        "favourableMeanDifference": favourable_difference,
        "bootstrapMeanDifferenceCi95": [ci_low, ci_high],
        "probabilityOfSuperiority": probability_of_superiority(
            coverage_values, random_values, direction=direction
        ),
        "inferenceSuppressed": False,
    }


def _exact_equality_override(
    left_rows: Sequence[MetricRow],
    right_rows: Sequence[MetricRow],
    *,
    simulated_metric: str,
    exact_metric: str,
    certificate_metric: str,
) -> dict | None:
    """Suppress Monte Carlo inference when exact certificates prove equal probabilities."""
    all_certified = all(
        row[certificate_metric] == 1.0 for row in [*left_rows, *right_rows]
    )
    exact_values = [row[exact_metric] for row in [*left_rows, *right_rows]]
    exact_equal = bool(exact_values) and max(exact_values) == min(exact_values)
    if not (all_certified and exact_equal):
        return None

    descriptive_difference = fmean(row[simulated_metric] for row in left_rows) - fmean(
        row[simulated_metric] for row in right_rows
    )
    return {
        "direction": "higher",
        "inferenceSuppressed": True,
        "exactProbabilityDifference": 0.0,
        "descriptiveSimulatedMeanDifference": descriptive_difference,
        "bootstrapMeanDifferenceCi95": None,
        "probabilityOfSuperiority": None,
        "reason": (
            "Both strategy distributions are exactly certified at the same Division-4-or-better "
            "probability. Any difference in the shared finite Monte Carlo draw sample is sampling "
            "noise, so bootstrap inference on that simulated difference is suppressed."
        ),
    }


def benchmark_portfolio_distributions(
    ticket_count: int = 10,
    *,
    coverage_portfolios: int = 50,
    random_portfolios: int = 200,
    trials: int = 5000,
    seed: int = 20260822,
    candidates_per_ticket: int = 120,
    bootstrap_resamples: int = 2000,
) -> dict:
    """Compare independently seeded coverage portfolios with a random-portfolio distribution.

    All portfolios are evaluated on the same simulated main-number draws. This common-random-
    numbers design reduces Monte Carlo noise when comparing portfolio structures. The benchmark
    tests lower-division coverage only: any same-sized set of distinct standard entries has the
    same Division 1 probability.
    """
    if ticket_count < 1:
        raise ValueError("ticket_count must be positive")
    if coverage_portfolios < 2 or random_portfolios < 2:
        raise ValueError("at least two portfolios are required in each distribution")
    if candidates_per_ticket < 20:
        raise ValueError("candidates_per_ticket must be at least 20")

    draws = _sample_main_draws(trials, seed=seed ^ 0x5A17_2026)
    coverage_rows = [
        _portfolio_row(
            generate_coverage_tickets(
                ticket_count,
                seed=f"benchmark:{seed}:coverage:{index}",
                candidates_per_ticket=candidates_per_ticket,
            ),
            draws,
        )
        for index in range(coverage_portfolios)
    ]
    random_rows = [
        _portfolio_row(
            generate_random_tickets(ticket_count, seed=f"benchmark:{seed}:random:{index}"),
            draws,
        )
        for index in range(random_portfolios)
    ]

    metric_directions = {
        "pairCoverageEfficiency": "higher",
        "tripleCoverageEfficiency": "higher",
        "quadCoverageEfficiency": "higher",
        "maxPairwiseOverlap": "lower",
        "uniqueNumbers": "higher",
        "anyPrizeBonferroniLowerBound": "higher",
        "division4CertifiedProbability": "higher",
        "division4GloballyOptimal": "higher",
        "anyPrizeRate": "higher",
        "division4OrBetterRate": "higher",
        "meanBestMainMatch": "higher",
    }
    metric_payload = {}
    for metric_index, (metric, direction) in enumerate(metric_directions.items()):
        coverage_values = [row[metric] for row in coverage_rows]
        random_values = [row[metric] for row in random_rows]
        metric_payload[metric] = {
            "coverage": distribution_summary(coverage_values),
            "random": distribution_summary(random_values),
            "comparison": _comparison(
                coverage_values,
                random_values,
                direction=direction,
                resamples=bootstrap_resamples,
                seed=seed + 1009 * (metric_index + 1),
            ),
        }

    return {
        "ticketCount": ticket_count,
        "coveragePortfolios": coverage_portfolios,
        "randomPortfolios": random_portfolios,
        "simulatedDraws": trials,
        "seed": seed,
        "candidatesPerTicket": candidates_per_ticket,
        "divisionOneProbability": ticket_count / 8_145_060,
        "divisionOneProbabilityEqual": True,
        "design": "independent portfolio seeds + shared simulated draw sample",
        "metrics": metric_payload,
        "note": (
            "Coverage and QuickPick distributions use the same number of distinct standard games. "
            "Division 1 probability is therefore identical. Positive lower-division differences "
            "measure portfolio diversification, not prediction of future draw numbers."
        ),
    }


def benchmark_probability_objectives(
    ticket_count: int = 10,
    *,
    portfolios_per_objective: int = 24,
    random_portfolios: int = 96,
    trials: int = 5000,
    seed: int = 20260822,
    candidates_per_ticket: int = 320,
    bootstrap_resamples: int = 2000,
) -> dict:
    """Compare subset, any-prize-bound and Division-4-bound objectives out of sample."""
    if portfolios_per_objective < 2 or random_portfolios < 2:
        raise ValueError("at least two portfolios are required in each distribution")
    draws = _sample_main_draws(trials, seed=seed ^ 0x0B1E_C71E)

    generators = {
        "coverage": generate_coverage_tickets,
        "anyPrizeBound": generate_any_prize_bound_tickets,
        "division4Bound": generate_division4_bound_tickets,
    }
    rows: dict[str, list[MetricRow]] = {}
    for strategy, generator in generators.items():
        rows[strategy] = [
            _portfolio_row(
                generator(
                    ticket_count,
                    seed=f"objective:{seed}:{strategy}:{index}",
                    candidates_per_ticket=candidates_per_ticket,
                ),
                draws,
            )
            for index in range(portfolios_per_objective)
        ]
    rows["random"] = [
        _portfolio_row(
            generate_random_tickets(ticket_count, seed=f"objective:{seed}:random:{index}"),
            draws,
        )
        for index in range(random_portfolios)
    ]

    reported_metrics = (
        "anyPrizeBonferroniLowerBound",
        "anyPrizeRate",
        "division4CertifiedProbability",
        "division4OrBetterRate",
        "division4GloballyOptimal",
        "tripleCoverageEfficiency",
        "maxPairwiseOverlap",
    )
    summaries = {
        strategy: {
            metric: distribution_summary([row[metric] for row in strategy_rows])
            for metric in reported_metrics
        }
        for strategy, strategy_rows in rows.items()
    }

    def compare(left: str, right: str, metric: str, direction: str, offset: int) -> dict:
        return _comparison(
            [row[metric] for row in rows[left]],
            [row[metric] for row in rows[right]],
            direction=direction,
            resamples=bootstrap_resamples,
            seed=seed + offset,
        )

    division4_simulated_comparison = _exact_equality_override(
        rows["division4Bound"],
        rows["coverage"],
        simulated_metric="division4OrBetterRate",
        exact_metric="division4CertifiedProbability",
        certificate_metric="division4GloballyOptimal",
    )
    if division4_simulated_comparison is None:
        division4_simulated_comparison = compare(
            "division4Bound", "coverage", "division4OrBetterRate", "higher", 202
        )

    comparisons = {
        "anyPrizeBoundVsCoverage": {
            "anyPrizeBonferroniLowerBound": compare(
                "anyPrizeBound", "coverage", "anyPrizeBonferroniLowerBound", "higher", 101
            ),
            "anyPrizeRate": compare(
                "anyPrizeBound", "coverage", "anyPrizeRate", "higher", 102
            ),
        },
        "division4BoundVsCoverage": {
            "division4CertifiedProbability": compare(
                "division4Bound", "coverage", "division4CertifiedProbability", "higher", 201
            ),
            "division4OrBetterRate": division4_simulated_comparison,
        },
        "coverageVsRandom": {
            "anyPrizeRate": compare("coverage", "random", "anyPrizeRate", "higher", 301),
            "division4OrBetterRate": compare(
                "coverage", "random", "division4OrBetterRate", "higher", 302
            ),
        },
    }

    return {
        "ticketCount": ticket_count,
        "portfoliosPerObjective": portfolios_per_objective,
        "randomPortfolios": random_portfolios,
        "simulatedDraws": trials,
        "seed": seed,
        "candidatesPerTicket": candidates_per_ticket,
        "divisionOneProbabilityEqual": True,
        "strategies": summaries,
        "comparisons": comparisons,
        "note": (
            "The bound-driven generators optimise exact pairwise-event mathematics, not simulated "
            "training outcomes. Monte Carlo draws are used only for out-of-sample comparison. When "
            "exact certificates prove two strategy distributions have the same true probability, "
            "Monte Carlo difference inference is suppressed rather than allowed to contradict the "
            "known combinatorial result."
        ),
    }
