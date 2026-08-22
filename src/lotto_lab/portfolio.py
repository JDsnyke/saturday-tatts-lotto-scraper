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


def exact_any_prize_probability(
    tickets: Sequence[Sequence[int]],
    *,
    max_tickets: int = 12,
) -> dict[str, float | int | bool | str | None]:
    """Compute the exact probability that at least one ticket wins any prize.

    Under the current Saturday Lotto prize structure, a standard game wins some prize
    exactly when it matches at least three of the six winning main numbers. Instead of
    enumerating all C(45, 6) winning sets, dynamic programming counts the complementary
    six-ball sets where every portfolio ticket finishes with at most two matches.

    Each ticket's surviving match count is encoded as one base-3 digit (0, 1 or 2).
    States that would create a third match for any ticket are discarded. The resulting
    count is exact integer combinatorics; no historical data or Monte Carlo is involved.
    """
    if max_tickets < 1:
        raise ValueError("max_tickets must be positive")
    if len(tickets) > max_tickets:
        raise ValueError(
            f"exact any-prize DP is capped at {max_tickets} tickets for predictable runtime"
        )

    normalized = [tuple(ticket) for ticket in tickets]
    for ticket in normalized:
        if len(ticket) != MAIN_COUNT or len(set(ticket)) != MAIN_COUNT:
            raise ValueError("every ticket must contain six distinct numbers")
        if any(number < 1 or number > BALL_COUNT for number in ticket):
            raise ValueError("ticket numbers must be between 1 and 45")

    total = combination_count()
    if not normalized:
        return {
            "ticketCount": 0,
            "totalWinningMainSets": total,
            "anyPrizeWinningMainSets": 0,
            "noPrizeWinningMainSets": total,
            "probability": 0.0,
            "odds": None,
            "exact": True,
            "algorithm": "base-3 complement dynamic programming",
        }

    ticket_sets = [set(ticket) for ticket in normalized]
    powers = [3**index for index in range(len(normalized))]
    memberships: list[tuple[int, ...]] = []
    for ball in range(1, BALL_COUNT + 1):
        memberships.append(
            tuple(index for index, ticket in enumerate(ticket_sets) if ball in ticket)
        )

    # dp[selected_balls][base3_match_code] = number of ways to reach the state.
    dp: list[dict[int, int]] = [dict() for _ in range(MAIN_COUNT + 1)]
    dp[0][0] = 1

    for members in memberships:
        next_dp = [bucket.copy() for bucket in dp]
        increment = sum(powers[index] for index in members)
        for selected in range(MAIN_COUNT):
            for code, ways in dp[selected].items():
                if members and any((code // powers[index]) % 3 == 2 for index in members):
                    continue
                next_code = code + increment
                bucket = next_dp[selected + 1]
                bucket[next_code] = bucket.get(next_code, 0) + ways
        dp = next_dp

    no_prize = sum(dp[MAIN_COUNT].values())
    any_prize = total - no_prize
    probability = any_prize / total
    return {
        "ticketCount": len(normalized),
        "totalWinningMainSets": total,
        "anyPrizeWinningMainSets": any_prize,
        "noPrizeWinningMainSets": no_prize,
        "probability": probability,
        "odds": (1 / probability) if probability else None,
        "exact": True,
        "algorithm": "base-3 complement dynamic programming",
    }


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
