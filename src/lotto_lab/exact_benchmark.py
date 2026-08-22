from __future__ import annotations

from statistics import fmean

from .benchmark import _comparison, distribution_summary
from .portfolio import exact_any_prize_probability
from .tickets import (
    generate_any_prize_bound_tickets,
    generate_coverage_tickets,
    generate_division4_bound_tickets,
    generate_random_tickets,
    ticket_metrics,
)


def _exact_row(tickets: list[tuple[int, ...]]) -> dict[str, float]:
    metrics = ticket_metrics(tickets)
    certificate = metrics["probabilityCertificates"]["anyPrize"]
    exact = exact_any_prize_probability(tickets)
    exact_probability = float(exact["probability"])
    lower_bound = float(certificate["bonferroniLowerBound"])
    return {
        "exactAnyPrizeProbability": exact_probability,
        "anyPrizeBonferroniLowerBound": lower_bound,
        "bonferroniGap": exact_probability - lower_bound,
        "tripleCoverageEfficiency": float(metrics["tripleCoverage"]["efficiency"]),
        "maxPairwiseOverlap": float(metrics["maxPairwiseOverlap"]),
    }


def benchmark_exact_any_prize_objectives(
    ticket_count: int = 10,
    *,
    portfolios_per_objective: int = 12,
    random_portfolios: int = 48,
    seed: int = 20260822,
    candidates_per_ticket: int = 320,
    bootstrap_resamples: int = 2000,
) -> dict:
    """Compare portfolio generators using exact any-prize union probabilities.

    The generated portfolio seeds intentionally match `benchmark_probability_objectives`
    so the exact benchmark can resolve Monte Carlo ambiguity for the same portfolios.
    Every individual portfolio probability is exact. Bootstrap intervals describe only
    variation across the deterministic portfolio-seed samples, not draw-sample noise.
    """
    if ticket_count < 1 or ticket_count > 12:
        raise ValueError("exact benchmark ticket_count must be between 1 and 12")
    if portfolios_per_objective < 2 or random_portfolios < 2:
        raise ValueError("at least two portfolios are required in each distribution")
    if candidates_per_ticket < 20:
        raise ValueError("candidates_per_ticket must be at least 20")

    generators = {
        "coverage": generate_coverage_tickets,
        "anyPrizeBound": generate_any_prize_bound_tickets,
        "division4Bound": generate_division4_bound_tickets,
    }
    rows: dict[str, list[dict[str, float]]] = {}
    for strategy, generator in generators.items():
        rows[strategy] = [
            _exact_row(
                generator(
                    ticket_count,
                    seed=f"objective:{seed}:{strategy}:{index}",
                    candidates_per_ticket=candidates_per_ticket,
                )
            )
            for index in range(portfolios_per_objective)
        ]
    rows["random"] = [
        _exact_row(
            generate_random_tickets(ticket_count, seed=f"objective:{seed}:random:{index}")
        )
        for index in range(random_portfolios)
    ]

    reported_metrics = (
        "exactAnyPrizeProbability",
        "anyPrizeBonferroniLowerBound",
        "bonferroniGap",
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

    comparisons = {
        "anyPrizeBoundVsCoverage": {
            "exactAnyPrizeProbability": compare(
                "anyPrizeBound", "coverage", "exactAnyPrizeProbability", "higher", 401
            ),
            "anyPrizeBonferroniLowerBound": compare(
                "anyPrizeBound", "coverage", "anyPrizeBonferroniLowerBound", "higher", 402
            ),
        },
        "division4BoundVsCoverage": {
            "exactAnyPrizeProbability": compare(
                "division4Bound", "coverage", "exactAnyPrizeProbability", "higher", 501
            ),
        },
        "coverageVsRandom": {
            "exactAnyPrizeProbability": compare(
                "coverage", "random", "exactAnyPrizeProbability", "higher", 601
            ),
        },
    }

    exact_means = {
        strategy: fmean(row["exactAnyPrizeProbability"] for row in strategy_rows)
        for strategy, strategy_rows in rows.items()
    }
    return {
        "ticketCount": ticket_count,
        "portfoliosPerObjective": portfolios_per_objective,
        "randomPortfolios": random_portfolios,
        "seed": seed,
        "candidatesPerTicket": candidates_per_ticket,
        "exact": True,
        "divisionOneProbabilityEqual": True,
        "portfolioSeedsMatchSimulatedObjectiveBenchmark": True,
        "strategies": summaries,
        "comparisons": comparisons,
        "bestExactMeanStrategy": max(exact_means, key=exact_means.get),
        "note": (
            "Each any-prize probability is an exact combinatorial result computed by complement "
            "dynamic programming. Bootstrap intervals describe portfolio-generator seed variation "
            "only; there is no Monte Carlo draw-sample uncertainty in this benchmark."
        ),
    }
