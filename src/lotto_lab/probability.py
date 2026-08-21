from __future__ import annotations

from math import comb, log, sqrt
from typing import Iterable

from .domain import BALL_COUNT, MAIN_COUNT


def combination_count(ball_count: int = BALL_COUNT, selected: int = MAIN_COUNT) -> int:
    return comb(ball_count, selected)


def division_one_probability(ticket_count: int = 1) -> float:
    if ticket_count < 0:
        raise ValueError("ticket_count must be non-negative")
    combinations = combination_count()
    if ticket_count > combinations:
        raise ValueError("ticket_count cannot exceed the number of unique combinations")
    return ticket_count / combinations


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
