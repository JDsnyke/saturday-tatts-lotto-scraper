from __future__ import annotations

from collections.abc import Sequence
from functools import cache
from itertools import combinations
from math import comb

from .domain import BALL_COUNT, MAIN_COUNT
from .probability import at_least_main_match_probability, combination_count


@cache
def pair_event_intersection_count(overlap: int, threshold: int) -> int:
    """Count winning main-number sets satisfying a match threshold for two tickets.

    Two six-number tickets with `overlap` shared numbers partition the 45 balls into
    shared, left-only, right-only and neither groups. Summing selections from those
    four groups gives the exact number of six-main-number draws in which both tickets
    match at least `threshold` main numbers.
    """
    if overlap < 0 or overlap > MAIN_COUNT:
        raise ValueError("overlap must be between 0 and 6")
    if threshold < 1 or threshold > MAIN_COUNT:
        raise ValueError("threshold must be between 1 and 6")

    shared = overlap
    left_only = MAIN_COUNT - overlap
    right_only = MAIN_COUNT - overlap
    neither = BALL_COUNT - (2 * MAIN_COUNT - overlap)
    favourable = 0

    for shared_selected in range(shared + 1):
        for left_selected in range(left_only + 1):
            for right_selected in range(right_only + 1):
                neither_selected = MAIN_COUNT - shared_selected - left_selected - right_selected
                if neither_selected < 0 or neither_selected > neither:
                    continue
                if shared_selected + left_selected < threshold:
                    continue
                if shared_selected + right_selected < threshold:
                    continue
                favourable += (
                    comb(shared, shared_selected)
                    * comb(left_only, left_selected)
                    * comb(right_only, right_selected)
                    * comb(neither, neither_selected)
                )
    return favourable


def pair_event_intersection_probability(overlap: int, threshold: int) -> float:
    return pair_event_intersection_count(overlap, threshold) / combination_count()


def portfolio_probability_certificate(
    tickets: Sequence[Sequence[int]],
    *,
    threshold: int,
) -> dict[str, float | int | bool | None]:
    """Return rigorous union bounds and an exact certificate when events are disjoint.

    The event is: at least one portfolio ticket matches `threshold` or more of the six
    winning main numbers. For threshold=3 this is equivalent to winning any Saturday
    Lotto prize division. For threshold=4 it is equivalent to Division 4 or better.

    Bonferroni gives P(union) >= S1 - S2 using exact single-ticket and pairwise event
    probabilities. The ordinary union bound gives P(union) <= S1. If every pairwise
    intersection is zero, both bounds meet, so the exact portfolio probability is S1
    and no same-sized portfolio can do better.
    """
    if threshold < 1 or threshold > MAIN_COUNT:
        raise ValueError("threshold must be between 1 and 6")

    normalized = [tuple(ticket) for ticket in tickets]
    for ticket in normalized:
        if len(ticket) != MAIN_COUNT or len(set(ticket)) != MAIN_COUNT:
            raise ValueError("every ticket must contain six distinct numbers")
        if any(number < 1 or number > BALL_COUNT for number in ticket):
            raise ValueError("ticket numbers must be between 1 and 45")

    single_probability = at_least_main_match_probability(threshold)
    first_order_sum = len(normalized) * single_probability
    second_order_sum = 0.0
    pairwise_disjoint = True
    maximum_overlap = 0

    for left, right in combinations(normalized, 2):
        overlap = len(set(left) & set(right))
        maximum_overlap = max(maximum_overlap, overlap)
        intersection = pair_event_intersection_probability(overlap, threshold)
        second_order_sum += intersection
        if intersection > 0:
            pairwise_disjoint = False

    lower_bound = max(0.0, first_order_sum - second_order_sum)
    upper_bound = min(1.0, first_order_sum)
    exact_probability = first_order_sum if pairwise_disjoint else None

    return {
        "threshold": threshold,
        "ticketCount": len(normalized),
        "singleTicketProbability": single_probability,
        "firstOrderUnionBound": upper_bound,
        "pairIntersectionProbabilitySum": second_order_sum,
        "bonferroniLowerBound": lower_bound,
        "pairwiseDisjointEvents": pairwise_disjoint,
        "maximumTicketOverlap": maximum_overlap,
        "exactProbability": exact_probability,
        "globallyOptimalForTicketCount": pairwise_disjoint,
    }
