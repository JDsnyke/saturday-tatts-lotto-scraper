from __future__ import annotations

import random
from collections import Counter
from math import sqrt

from .domain import BALL_COUNT, MAIN_COUNT, Draw
from .tickets import Ticket, generate_coverage_tickets, generate_random_tickets, ticket_metrics


def best_main_match(tickets: list[Ticket], draw: tuple[int, ...]) -> int:
    draw_set = set(draw)
    return max((len(draw_set & set(ticket)) for ticket in tickets), default=0)


def ticket_prize_division(
    ticket: Ticket,
    main: tuple[int, ...],
    supplementary: tuple[int, ...],
) -> int:
    """Return 1..6 for the ticket's highest Saturday Lotto prize division, else 0."""
    ticket_set = set(ticket)
    winning_matches = len(ticket_set & set(main))
    supplementary_matches = len(ticket_set & set(supplementary))
    if winning_matches == 6:
        return 1
    if winning_matches == 5 and supplementary_matches >= 1:
        return 2
    if winning_matches == 5:
        return 3
    if winning_matches == 4:
        return 4
    if winning_matches == 3 and supplementary_matches >= 1:
        return 5
    if winning_matches == 3:
        return 6
    return 0


def best_prize_division(
    tickets: list[Ticket],
    main: tuple[int, ...],
    supplementary: tuple[int, ...],
) -> int:
    divisions = [ticket_prize_division(ticket, main, supplementary) for ticket in tickets]
    winners = [division for division in divisions if division]
    return min(winners, default=0)


def wilson_interval(successes: int, trials: int, z: float = 1.96) -> tuple[float, float]:
    if trials <= 0:
        return (0.0, 0.0)
    p = successes / trials
    denominator = 1 + z * z / trials
    centre = (p + z * z / (2 * trials)) / denominator
    margin = z * sqrt((p * (1 - p) + z * z / (4 * trials)) / trials) / denominator
    return (max(0.0, centre - margin), min(1.0, centre + margin))


def simulate_ticket_set(
    tickets: list[Ticket],
    *,
    trials: int = 50_000,
    seed: int = 20260822,
) -> dict:
    if trials < 1:
        raise ValueError("trials must be positive")
    rng = random.Random(seed)
    counts: Counter[int] = Counter()
    prize_counts: Counter[int] = Counter()
    population = list(range(1, BALL_COUNT + 1))
    for _ in range(trials):
        balls = tuple(rng.sample(population, MAIN_COUNT + 2))
        main = balls[:MAIN_COUNT]
        supplementary = balls[MAIN_COUNT:]
        counts[best_main_match(tickets, main)] += 1
        prize_counts[best_prize_division(tickets, main, supplementary)] += 1

    thresholds = {}
    for threshold in (3, 4, 5, 6):
        successes = sum(count for matches, count in counts.items() if matches >= threshold)
        low, high = wilson_interval(successes, trials)
        thresholds[str(threshold)] = {
            "hits": successes,
            "probability": successes / trials,
            "ci95": [low, high],
        }
    prize_hits = trials - prize_counts[0]
    any_low, any_high = wilson_interval(prize_hits, trials)
    division_four_or_better = sum(prize_counts[division] for division in range(1, 5))
    div4_low, div4_high = wilson_interval(division_four_or_better, trials)
    return {
        "trials": trials,
        "seed": seed,
        "bestMatchHistogram": {str(k): counts[k] for k in range(MAIN_COUNT + 1)},
        "atLeast": thresholds,
        "bestPrizeDivisionHistogram": {str(k): prize_counts[k] for k in range(7)},
        "anyPrize": {
            "hits": prize_hits,
            "probability": prize_hits / trials,
            "ci95": [any_low, any_high],
        },
        "division4OrBetter": {
            "hits": division_four_or_better,
            "probability": division_four_or_better / trials,
            "ci95": [div4_low, div4_high],
        },
    }


def compare_strategies(
    ticket_count: int = 10,
    *,
    trials: int = 50_000,
    seed: int = 20260822,
) -> dict:
    coverage = generate_coverage_tickets(ticket_count, seed=f"coverage:{seed}")
    random_tickets = generate_random_tickets(ticket_count, seed=f"random:{seed}")
    return {
        "ticketCount": ticket_count,
        "note": (
            "Division 1 probability is identical for any same-sized set of distinct entries. "
            "Simulation compares lower-order main-number match coverage only."
        ),
        "coverage": {
            "metrics": ticket_metrics(coverage),
            "simulation": simulate_ticket_set(coverage, trials=trials, seed=seed),
        },
        "random": {
            "metrics": ticket_metrics(random_tickets),
            "simulation": simulate_ticket_set(random_tickets, trials=trials, seed=seed),
        },
    }


def walk_forward_backtest(
    draws: list[Draw],
    *,
    ticket_count: int = 10,
    max_steps: int = 120,
    seed: int = 20260822,
) -> dict:
    """Evaluate each strategy only against draws that occur after its seed state.

    The generators do not use historical frequencies; the previous draw date is used
    only to make each portfolio reproducible. This is therefore a leakage-free
    historical comparison of portfolio structure, not a predictive backtest.
    """
    ordered = sorted(draws, key=lambda draw: draw.date)
    if len(ordered) < 2:
        raise ValueError("at least two draws are required")
    evaluation = ordered[-min(max_steps, len(ordered) - 1):]
    start_index = len(ordered) - len(evaluation)
    results = {
        "coverage": Counter(),
        "random": Counter(),
    }
    prize_results = {
        "coverage": Counter(),
        "random": Counter(),
    }
    triple_efficiency = {"coverage": [], "random": []}

    for offset, draw in enumerate(evaluation, start=start_index):
        previous = ordered[offset - 1]
        coverage = generate_coverage_tickets(
            ticket_count, seed=f"wf:{seed}:{previous.date}:coverage", candidates_per_ticket=120
        )
        random_tickets = generate_random_tickets(
            ticket_count, seed=f"wf:{seed}:{previous.date}:random"
        )
        for name, tickets in (("coverage", coverage), ("random", random_tickets)):
            best = best_main_match(tickets, draw.main)
            results[name][best] += 1
            prize_results[name][best_prize_division(tickets, draw.main, draw.supplementary)] += 1
            triple_efficiency[name].append(
                float(ticket_metrics(tickets)["tripleCoverage"]["efficiency"])
            )

    payload = {
        "steps": len(evaluation),
        "ticketCount": ticket_count,
        "note": (
            "Historical draws are used only as out-of-sample outcomes. No historical frequency "
            "or recency signal is fed into ticket generation."
        ),
    }
    for name in ("coverage", "random"):
        histogram = results[name]
        prize_histogram = prize_results[name]
        payload[name] = {
            "bestMatchHistogram": {str(k): histogram[k] for k in range(MAIN_COUNT + 1)},
            "bestPrizeDivisionHistogram": {str(k): prize_histogram[k] for k in range(7)},
            "atLeast3Rate": sum(v for k, v in histogram.items() if k >= 3) / len(evaluation),
            "atLeast4Rate": sum(v for k, v in histogram.items() if k >= 4) / len(evaluation),
            "anyPrizeRate": (len(evaluation) - prize_histogram[0]) / len(evaluation),
            "division4OrBetterRate": (
                sum(prize_histogram[k] for k in range(1, 5)) / len(evaluation)
            ),
            "meanTripleCoverageEfficiency": sum(triple_efficiency[name]) / len(evaluation),
        }
    return payload
