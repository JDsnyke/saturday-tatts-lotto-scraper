from __future__ import annotations

import hashlib
import random
from collections.abc import Sequence

from .domain import BALL_COUNT, MAIN_COUNT
from .portfolio import exact_any_prize_probability, portfolio_probability_certificate
from .tickets import Ticket, generate_coverage_tickets, subset_coverage


def _rng(seed: str | int | None) -> random.Random:
    if seed is None:
        return random.SystemRandom()
    if isinstance(seed, str):
        digest = hashlib.sha256(seed.encode("utf-8")).digest()
        seed = int.from_bytes(digest[:16], "big")
    return random.Random(seed)


def _validate_portfolio(tickets: Sequence[Sequence[int]]) -> list[Ticket]:
    normalized: list[Ticket] = []
    for ticket in tickets:
        canonical = tuple(sorted(ticket))
        if len(canonical) != MAIN_COUNT or len(set(canonical)) != MAIN_COUNT:
            raise ValueError("every ticket must contain six distinct numbers")
        if any(number < 1 or number > BALL_COUNT for number in canonical):
            raise ValueError("ticket numbers must be between 1 and 45")
        normalized.append(canonical)
    if not normalized:
        raise ValueError("at least one ticket is required")
    if len(set(normalized)) != len(normalized):
        raise ValueError("portfolio tickets must be distinct")
    return normalized


def _one_swap_neighbours(tickets: Sequence[Ticket]) -> list[tuple[tuple[Ticket, ...], dict[str, int]]]:
    """Enumerate unique portfolios reachable by one number replacement in one ticket."""
    current = tuple(tickets)
    current_set = set(current)
    neighbours: dict[tuple[Ticket, ...], dict[str, int]] = {}

    for ticket_index, ticket in enumerate(current):
        ticket_numbers = set(ticket)
        for removed in ticket:
            remaining = ticket_numbers - {removed}
            for added in range(1, BALL_COUNT + 1):
                if added in ticket_numbers:
                    continue
                replacement = tuple(sorted((*remaining, added)))
                if replacement in current_set and replacement != ticket:
                    continue
                candidate = list(current)
                candidate[ticket_index] = replacement
                candidate_tuple = tuple(candidate)
                canonical_portfolio = tuple(sorted(candidate_tuple))
                if canonical_portfolio in neighbours:
                    continue
                neighbours[canonical_portfolio] = {
                    "ticketIndex": ticket_index,
                    "removed": removed,
                    "added": added,
                }
    return [(portfolio, move) for portfolio, move in neighbours.items()]


def _screen_score(tickets: Sequence[Ticket]) -> tuple[float, float, float, int]:
    any_prize = portfolio_probability_certificate(tickets, threshold=3)
    triples = subset_coverage(tickets, 3)
    pairs = subset_coverage(tickets, 2)
    return (
        float(any_prize["bonferroniLowerBound"]),
        float(triples["efficiency"]),
        float(pairs["efficiency"]),
        -int(any_prize["maximumTicketOverlap"]),
    )


def optimise_any_prize_exact(
    tickets: Sequence[Sequence[int]],
    *,
    seed: str | int | None = None,
    iterations: int = 2,
    exact_shortlist: int = 4,
    exploration_candidates: int = 1,
    preserve_division4_optimality: bool = True,
) -> dict:
    """Monotonic one-swap local search with exact any-prize acceptance.

    Cheap exact pair-intersection bounds screen the full one-swap neighbourhood.
    Only shortlisted portfolios are passed to the more expensive exact dynamic
    program. A move is accepted only when its integer favourable-set count is
    strictly larger than the current count.

    If the starting portfolio has an exact/global-optimal Division-4+ certificate,
    that certificate is preserved by default. Equal ticket count and distinctness
    preserve Division 1 probability automatically.
    """
    portfolio = _validate_portfolio(tickets)
    if iterations < 0:
        raise ValueError("iterations must be non-negative")
    if exact_shortlist < 1:
        raise ValueError("exact_shortlist must be at least 1")
    if exploration_candidates < 0:
        raise ValueError("exploration_candidates must be non-negative")

    rng = _rng(seed)
    baseline_exact = exact_any_prize_probability(portfolio)
    current_exact = baseline_exact
    baseline_div4 = portfolio_probability_certificate(portfolio, threshold=4)
    require_div4_certificate = bool(
        preserve_division4_optimality and baseline_div4["globallyOptimalForTicketCount"]
    )

    history: list[dict] = []
    exact_evaluations = 1
    screened_neighbours = 0

    for iteration in range(1, iterations + 1):
        screened: list[tuple[tuple[float, float, float, int], float, tuple[Ticket, ...], dict[str, int]]] = []
        for neighbour, move in _one_swap_neighbours(portfolio):
            if require_div4_certificate:
                division4 = portfolio_probability_certificate(neighbour, threshold=4)
                if not division4["globallyOptimalForTicketCount"]:
                    continue
            score = _screen_score(neighbour)
            screened.append((score, rng.random(), neighbour, move))

        screened_neighbours += len(screened)
        if not screened:
            break
        screened.sort(key=lambda row: (row[0], row[1]), reverse=True)

        selected = screened[:exact_shortlist]
        remainder = screened[exact_shortlist:]
        if exploration_candidates and remainder:
            sample_size = min(exploration_candidates, len(remainder))
            selected.extend(rng.sample(remainder, sample_size))

        best = None
        best_count = int(current_exact["anyPrizeWinningMainSets"])
        for score, _tie, candidate, move in selected:
            exact = exact_any_prize_probability(candidate)
            exact_evaluations += 1
            favourable_count = int(exact["anyPrizeWinningMainSets"])
            if favourable_count > best_count:
                best_count = favourable_count
                best = (candidate, move, score, exact)

        if best is None:
            break

        candidate, move, score, exact = best
        before_count = int(current_exact["anyPrizeWinningMainSets"])
        portfolio = list(candidate)
        current_exact = exact
        history.append(
            {
                "iteration": iteration,
                "move": move,
                "beforeAnyPrizeWinningMainSets": before_count,
                "afterAnyPrizeWinningMainSets": best_count,
                "improvementWinningMainSets": best_count - before_count,
                "screenBonferroniLowerBound": score[0],
                "exactProbability": exact["probability"],
            }
        )

    final_div4 = portfolio_probability_certificate(portfolio, threshold=4)
    baseline_count = int(baseline_exact["anyPrizeWinningMainSets"])
    final_count = int(current_exact["anyPrizeWinningMainSets"])

    return {
        "tickets": [list(ticket) for ticket in portfolio],
        "baselineExactAnyPrize": baseline_exact,
        "finalExactAnyPrize": current_exact,
        "improvementWinningMainSets": final_count - baseline_count,
        "improvementProbability": (final_count - baseline_count) / int(current_exact["totalWinningMainSets"]),
        "acceptedMoves": len(history),
        "iterationsRequested": iterations,
        "exactEvaluations": exact_evaluations,
        "screenedNeighbours": screened_neighbours,
        "preservedDivision4Optimality": (
            not require_div4_certificate or bool(final_div4["globallyOptimalForTicketCount"])
        ),
        "division4CertificateWasRequired": require_div4_certificate,
        "history": history,
        "algorithm": "one-swap local search; Bonferroni screening; exact-DP monotonic acceptance",
    }


def generate_exact_local_tickets(
    count: int,
    seed: str | int | None = None,
    *,
    candidates_per_ticket: int = 320,
    iterations: int = 2,
    exact_shortlist: int = 4,
    exploration_candidates: int = 1,
) -> list[Ticket]:
    """Generate Coverage tickets, then improve or retain them on exact any-prize probability."""
    baseline = generate_coverage_tickets(
        count,
        seed=seed,
        candidates_per_ticket=candidates_per_ticket,
    )
    result = optimise_any_prize_exact(
        baseline,
        seed=f"{seed}:exact-local" if seed is not None else None,
        iterations=iterations,
        exact_shortlist=exact_shortlist,
        exploration_candidates=exploration_candidates,
        preserve_division4_optimality=True,
    )
    return [tuple(ticket) for ticket in result["tickets"]]
