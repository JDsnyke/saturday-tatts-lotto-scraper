from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from datetime import UTC, datetime
from itertools import combinations

from .benchmark import benchmark_portfolio_distributions
from .domain import BALL_COUNT, DIVISION_ONE_COMBINATIONS, MAIN_COUNT, SUPPLEMENTARY_COUNT, Draw
from .probability import (
    any_prize_probability,
    at_least_main_match_probability,
    chi_square_uniform,
    expected_number_count,
    main_match_distribution,
    normalized_entropy,
    number_z_score,
    odds_from_probability,
    prize_division_probabilities,
    system_entry_combinations,
)
from .simulation import compare_strategies, walk_forward_backtest
from .tickets import generate_coverage_tickets, ticket_metrics


def build_statistics(draws: Sequence[Draw], *, generated_at: datetime | None = None) -> dict:
    if not draws:
        raise ValueError("at least one draw is required")
    ordered = sorted(draws, key=lambda draw: draw.date)
    generated_at = generated_at or datetime.now(UTC)

    main_counts = Counter(number for draw in ordered for number in draw.main)
    supp_counts = Counter(number for draw in ordered for number in draw.supplementary)
    draw_count = len(ordered)
    expected = expected_number_count(draw_count)

    last_seen: dict[int, int] = {}
    for index, draw in enumerate(ordered):
        for number in draw.main:
            last_seen[number] = index

    number_rows = []
    for number in range(1, BALL_COUNT + 1):
        count = main_counts[number]
        last_index = last_seen.get(number)
        number_rows.append(
            {
                "number": number,
                "mainCount": count,
                "supplementaryCount": supp_counts[number],
                "mainRate": round(count / draw_count, 8),
                "zScore": round(number_z_score(count, draw_count), 4),
                "drawsSinceMain": None if last_index is None else len(ordered) - 1 - last_index,
                "lastMainDate": None if last_index is None else ordered[last_index].date.isoformat(),
            }
        )

    pair_counts: Counter[tuple[int, int]] = Counter()
    for draw in ordered:
        pair_counts.update(tuple(sorted(pair)) for pair in combinations(draw.main, 2))
    expected_pair_count = draw_count * (MAIN_COUNT / BALL_COUNT) * ((MAIN_COUNT - 1) / (BALL_COUNT - 1))
    top_pairs = []
    for pair, count in sorted(pair_counts.items(), key=lambda item: (-item[1], item[0]))[:20]:
        top_pairs.append(
            {
                "numbers": list(pair),
                "count": count,
                "liftVsExpected": round(count / expected_pair_count, 4) if expected_pair_count else 0.0,
            }
        )

    frequency_values = [main_counts[number] for number in range(1, BALL_COUNT + 1)]
    reference_seed = f"{ordered[-1].date.isoformat()}:{draw_count}:coverage-v3"
    reference_tickets = generate_coverage_tickets(10, seed=reference_seed)
    match_distribution = main_match_distribution()
    system_rows = [
        {
            "selectedNumbers": selected,
            "standardCombinations": system_entry_combinations(selected),
            "divisionOneProbability": system_entry_combinations(selected) / DIVISION_ONE_COMBINATIONS,
        }
        for selected in range(6, 21)
    ]

    return {
        "schemaVersion": 3,
        "generatedAt": generated_at.isoformat().replace("+00:00", "Z"),
        "game": {
            "name": "Saturday Lotto / TattsLotto",
            "ballCount": BALL_COUNT,
            "mainNumbers": MAIN_COUNT,
            "supplementaryNumbers": SUPPLEMENTARY_COUNT,
            "divisionOneCombinations": DIVISION_ONE_COMBINATIONS,
            "divisionOneOdds": f"1 in {DIVISION_ONE_COMBINATIONS:,}",
        },
        "dataset": {
            "drawCount": draw_count,
            "firstDraw": ordered[0].date.isoformat(),
            "lastDraw": ordered[-1].date.isoformat(),
            "mainObservations": draw_count * MAIN_COUNT,
            "supplementaryObservations": draw_count * SUPPLEMENTARY_COUNT,
        },
        "probabilityModel": {
            "prizeDivisions": prize_division_probabilities(),
            "anyPrizeProbability": any_prize_probability(),
            "anyPrizeOdds": odds_from_probability(any_prize_probability()),
            "mainMatchDistribution": match_distribution,
            "atLeastThreeMainProbability": at_least_main_match_probability(3),
            "atLeastThreeMainOdds": odds_from_probability(at_least_main_match_probability(3)),
            "systemEntries": system_rows,
        },
        "fairnessDiagnostics": {
            "expectedMainCountPerNumber": round(expected, 4),
            "chiSquareUniform": round(chi_square_uniform(frequency_values), 4),
            "normalizedEntropy": round(normalized_entropy(frequency_values), 6),
            "maxAbsoluteZScore": round(max(abs(row["zScore"]) for row in number_rows), 4),
            "interpretation": (
                "Historical frequency is descriptive only. Independent random draws do not make a number "
                "more or less likely next week because it is hot, cold, overdue, or recently drawn."
            ),
        },
        "numbers": number_rows,
        "topHistoricalPairs": top_pairs,
        "draws": [
            {
                "date": draw.date.isoformat(),
                "main": list(draw.main),
                "supplementary": list(draw.supplementary),
            }
            for draw in reversed(ordered)
        ],
        "referenceCoverageSet": {
            "seed": reference_seed,
            "tickets": [list(ticket) for ticket in reference_tickets],
            "metrics": ticket_metrics(reference_tickets),
            "note": (
                "Coverage mode maximises new 4-, 3- and 2-number subsets across multiple entries. "
                "It does not change the odds of any individual six-number combination."
            ),
        },
        "referenceSimulation": compare_strategies(10, trials=20_000, seed=20260822),
        "referenceBacktest": walk_forward_backtest(list(ordered), ticket_count=10, max_steps=52),
        "referenceBenchmark": benchmark_portfolio_distributions(
            10,
            coverage_portfolios=32,
            random_portfolios=128,
            trials=2500,
            seed=20260822,
            candidates_per_ticket=120,
            bootstrap_resamples=1200,
        ),
    }
