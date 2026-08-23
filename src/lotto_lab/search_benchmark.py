from __future__ import annotations

import random
from statistics import fmean

from .benchmark import distribution_summary
from .optimizer import optimise_any_prize_exact
from .portfolio import exact_any_prize_probability, portfolio_probability_certificate
from .tickets import generate_coverage_tickets


def _quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def _paired_bootstrap_mean_ci(
    differences: list[float],
    *,
    resamples: int,
    seed: int,
) -> tuple[float, float]:
    if not differences:
        raise ValueError("at least one paired difference is required")
    if resamples < 100:
        raise ValueError("resamples must be at least 100")
    rng = random.Random(seed)
    means = [
        fmean(rng.choice(differences) for _ in differences)
        for _ in range(resamples)
    ]
    return _quantile(means, 0.025), _quantile(means, 0.975)


def benchmark_exact_local_search(
    ticket_count: int = 10,
    *,
    portfolios: int = 8,
    seed: int = 20260822,
    candidates_per_ticket: int = 320,
    iterations: int = 2,
    exact_shortlist: int = 4,
    exploration_candidates: int = 1,
    bootstrap_resamples: int = 1200,
) -> dict:
    """Paired exact benchmark: Coverage start vs its own exact-guided local-search result."""
    if portfolios < 2:
        raise ValueError("at least two portfolios are required")

    rows = []
    for index in range(portfolios):
        coverage_seed = f"objective:{seed}:coverage:{index}"
        baseline = generate_coverage_tickets(
            ticket_count,
            seed=coverage_seed,
            candidates_per_ticket=candidates_per_ticket,
        )
        baseline_exact = exact_any_prize_probability(baseline)
        baseline_div4 = portfolio_probability_certificate(baseline, threshold=4)
        result = optimise_any_prize_exact(
            baseline,
            seed=f"exact-local:{seed}:{index}",
            iterations=iterations,
            exact_shortlist=exact_shortlist,
            exploration_candidates=exploration_candidates,
            preserve_division4_optimality=True,
        )
        final_tickets = [tuple(ticket) for ticket in result["tickets"]]
        final_exact = result["finalExactAnyPrize"]
        final_div4 = portfolio_probability_certificate(final_tickets, threshold=4)
        baseline_count = int(baseline_exact["anyPrizeWinningMainSets"])
        final_count = int(final_exact["anyPrizeWinningMainSets"])
        if final_count < baseline_count:
            raise AssertionError("exact local search worsened the objective")
        if baseline_div4["globallyOptimalForTicketCount"] and not final_div4[
            "globallyOptimalForTicketCount"
        ]:
            raise AssertionError("exact local search lost an existing Division-4+ optimum certificate")

        rows.append(
            {
                "index": index,
                "coverageSeed": coverage_seed,
                "baselineExactAnyPrizeProbability": float(baseline_exact["probability"]),
                "finalExactAnyPrizeProbability": float(final_exact["probability"]),
                "improvementProbability": (final_count - baseline_count)
                / int(final_exact["totalWinningMainSets"]),
                "improvementWinningMainSets": final_count - baseline_count,
                "acceptedMoves": int(result["acceptedMoves"]),
                "exactEvaluations": int(result["exactEvaluations"]),
                "screenedNeighbours": int(result["screenedNeighbours"]),
                "baselineDivision4Optimal": bool(
                    baseline_div4["globallyOptimalForTicketCount"]
                ),
                "finalDivision4Optimal": bool(final_div4["globallyOptimalForTicketCount"]),
            }
        )

    improvements = [row["improvementProbability"] for row in rows]
    improvement_counts = [float(row["improvementWinningMainSets"]) for row in rows]
    baseline_probabilities = [row["baselineExactAnyPrizeProbability"] for row in rows]
    final_probabilities = [row["finalExactAnyPrizeProbability"] for row in rows]
    ci_low, ci_high = _paired_bootstrap_mean_ci(
        improvements,
        resamples=bootstrap_resamples,
        seed=seed ^ 0x214E_A7C7,
    )
    improved = sum(value > 0 for value in improvements)
    all_d4_preserved = all(
        (not row["baselineDivision4Optimal"]) or row["finalDivision4Optimal"]
        for row in rows
    )

    return {
        "ticketCount": ticket_count,
        "portfolioPairs": portfolios,
        "seed": seed,
        "candidatesPerTicket": candidates_per_ticket,
        "iterations": iterations,
        "exactShortlist": exact_shortlist,
        "explorationCandidates": exploration_candidates,
        "exact": True,
        "pairedDesign": True,
        "divisionOneProbabilityEqual": True,
        "baseline": distribution_summary(baseline_probabilities),
        "final": distribution_summary(final_probabilities),
        "improvementProbability": distribution_summary(improvements),
        "improvementWinningMainSets": distribution_summary(improvement_counts),
        "pairedMeanImprovementCi95": [ci_low, ci_high],
        "improvedPortfolioFraction": improved / portfolios,
        "unchangedPortfolioFraction": (portfolios - improved) / portfolios,
        "allExactImprovementsNonNegative": all(value >= 0 for value in improvements),
        "allExistingDivision4OptimaPreserved": all_d4_preserved,
        "rows": rows,
        "note": (
            "Each improved portfolio starts from its paired Coverage portfolio. Bonferroni is used "
            "only for neighbour screening; a move is accepted only when exact dynamic-programming "
            "evaluation increases the integer any-prize winning-main-set count. Existing exact "
            "Division-4+ global-optimality certificates are preserved. No global any-prize optimum "
            "is claimed."
        ),
    }
