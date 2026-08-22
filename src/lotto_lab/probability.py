from __future__ import annotations

from collections.abc import Iterable
from math import comb, log, sqrt

from .domain import BALL_COUNT, MAIN_COUNT, SUPPLEMENTARY_COUNT


def combination_count(ball_count: int = BALL_COUNT, selected: int = MAIN_COUNT) -> int:
    return comb(ball_count, selected)


def division_one_probability(ticket_count: int = 1) -> float:
    if ticket_count < 0:
        raise ValueError("ticket_count must be non-negative")
    combinations = combination_count()
    if ticket_count > combinations:
        raise ValueError("ticket_count cannot exceed the number of unique combinations")
    return ticket_count / combinations


def cumulative_division_one_probability(ticket_count: int, draws: int) -> float:
    """Chance of >=1 Division 1 over independent draws using distinct tickets each draw."""
    if draws < 0:
        raise ValueError("draws must be non-negative")
    per_draw = division_one_probability(ticket_count)
    return 1.0 - (1.0 - per_draw) ** draws


def system_entry_combinations(selected_numbers: int) -> int:
    if selected_numbers < MAIN_COUNT or selected_numbers > 20:
        raise ValueError("system entry must select between 6 and 20 numbers")
    return comb(selected_numbers, MAIN_COUNT)


def main_match_probability(matches: int) -> float:
    """Exact probability a fixed standard ticket matches exactly `matches` main balls."""
    if matches < 0 or matches > MAIN_COUNT:
        return 0.0
    misses = MAIN_COUNT - matches
    if misses > BALL_COUNT - MAIN_COUNT:
        return 0.0
    favourable = comb(MAIN_COUNT, matches) * comb(BALL_COUNT - MAIN_COUNT, misses)
    return favourable / combination_count()


def main_match_distribution() -> list[dict[str, float | int]]:
    return [
        {"matches": matches, "probability": main_match_probability(matches)}
        for matches in range(MAIN_COUNT + 1)
    ]


def at_least_main_match_probability(matches: int) -> float:
    if matches <= 0:
        return 1.0
    if matches > MAIN_COUNT:
        return 0.0
    return sum(main_match_probability(k) for k in range(matches, MAIN_COUNT + 1))


def odds_from_probability(probability: float) -> float | None:
    if probability <= 0:
        return None
    return 1.0 / probability


def ticket_category_probability(main_matches: int, supplementary_matches: int) -> float:
    """Probability a fixed six-number ticket has an exact main/supplementary match category."""
    if main_matches < 0 or main_matches > MAIN_COUNT:
        return 0.0
    if supplementary_matches < 0 or supplementary_matches > SUPPLEMENTARY_COUNT:
        return 0.0
    other_matches = MAIN_COUNT - main_matches - supplementary_matches
    other_ball_count = BALL_COUNT - MAIN_COUNT - SUPPLEMENTARY_COUNT
    if other_matches < 0 or other_matches > other_ball_count:
        return 0.0
    favourable = (
        comb(MAIN_COUNT, main_matches)
        * comb(SUPPLEMENTARY_COUNT, supplementary_matches)
        * comb(other_ball_count, other_matches)
    )
    return favourable / combination_count()


def prize_division_probabilities() -> list[dict[str, float | int | str]]:
    """Exact standard-entry probabilities under the current six-division Saturday Lotto rules."""
    divisions = [
        (1, "6 winning", ticket_category_probability(6, 0)),
        (2, "5 winning + supplementary", ticket_category_probability(5, 1)),
        (3, "5 winning", ticket_category_probability(5, 0)),
        (4, "4 winning", sum(ticket_category_probability(4, s) for s in range(3))),
        (
            5,
            "3 winning + supplementary",
            ticket_category_probability(3, 1) + ticket_category_probability(3, 2),
        ),
        (6, "3 winning", ticket_category_probability(3, 0)),
    ]
    return [
        {
            "division": division,
            "requirement": requirement,
            "probability": probability,
            "odds": odds_from_probability(probability),
        }
        for division, requirement, probability in divisions
    ]


def any_prize_probability() -> float:
    return sum(float(row["probability"]) for row in prize_division_probabilities())


def expected_number_count(draw_count: int) -> float:
    return draw_count * MAIN_COUNT / BALL_COUNT


def number_z_score(observed: int, draw_count: int) -> float:
    if draw_count <= 0:
        return 0.0
    p = MAIN_COUNT / BALL_COUNT
    expected = draw_count * p
    variance = draw_count * p * (1 - p)
    return 0.0 if variance == 0 else (observed - expected) / sqrt(variance)


def normalized_entropy(counts: Iterable[int]) -> float:
    values = [max(0, int(value)) for value in counts]
    total = sum(values)
    if total == 0:
        return 0.0
    probabilities = [value / total for value in values if value]
    entropy = -sum(p * log(p) for p in probabilities)
    return entropy / log(len(values)) if len(values) > 1 else 1.0


def chi_square_uniform(counts: Iterable[int]) -> float:
    values = [int(value) for value in counts]
    if not values or sum(values) == 0:
        return 0.0
    expected = sum(values) / len(values)
    return sum((value - expected) ** 2 / expected for value in values)
