from __future__ import annotations

import hashlib
import random
from collections import Counter
from collections.abc import Iterable
from itertools import combinations
from math import comb

from .domain import BALL_COUNT, MAIN_COUNT
from .portfolio import pair_event_intersection_count, portfolio_probability_certificate
from .probability import division_one_probability

Ticket = tuple[int, ...]


def _rng(seed: str | int | None = None) -> random.Random:
    if seed is None:
        return random.SystemRandom()
    if isinstance(seed, str):
        digest = hashlib.sha256(seed.encode("utf-8")).digest()
        seed = int.from_bytes(digest[:16], "big")
    return random.Random(seed)


def _random_ticket(rng: random.Random) -> Ticket:
    return tuple(sorted(rng.sample(range(1, BALL_COUNT + 1), MAIN_COUNT)))


def generate_random_tickets(count: int, seed: str | int | None = None) -> list[Ticket]:
    _validate_count(count)
    rng = _rng(seed)
    seen: set[Ticket] = set()
    tickets: list[Ticket] = []
    while len(tickets) < count:
        ticket = _random_ticket(rng)
        if ticket not in seen:
            seen.add(ticket)
            tickets.append(ticket)
    return tickets


def subset_coverage(tickets: Iterable[Ticket], subset_size: int) -> dict[str, float | int]:
    if subset_size < 1 or subset_size > MAIN_COUNT:
        raise ValueError("subset_size must be between 1 and 6")
    ticket_list = list(tickets)
    covered = {
        subset
        for ticket in ticket_list
        for subset in combinations(ticket, subset_size)
    }
    placements = len(ticket_list) * comb(MAIN_COUNT, subset_size)
    universe = comb(BALL_COUNT, subset_size)
    simple_upper_bound = min(universe, placements)
    repeated = placements - len(covered)
    return {
        "subsetSize": subset_size,
        "unique": len(covered),
        "placements": placements,
        "repeated": repeated,
        "simpleUpperBound": simple_upper_bound,
        "efficiency": (len(covered) / placements) if placements else 0.0,
        "universeCoverage": len(covered) / universe,
    }


def _candidate_structure(
    candidate: Ticket,
    tickets: list[Ticket],
    usage: Counter[int],
    covered: dict[int, set[tuple[int, ...]]],
) -> tuple[int, int, int, int, int, list[int]]:
    new4 = sum(1 for subset in combinations(candidate, 4) if subset not in covered[4])
    new3 = sum(1 for subset in combinations(candidate, 3) if subset not in covered[3])
    new2 = sum(1 for subset in combinations(candidate, 2) if subset not in covered[2])
    candidate_set = set(candidate)
    overlaps = [len(candidate_set & set(ticket)) for ticket in tickets]
    max_overlap = max(overlaps, default=0)
    usage_cost = sum(usage[number] for number in candidate)
    return new4, new3, new2, max_overlap, usage_cost, overlaps


def generate_coverage_tickets(
    count: int,
    seed: str | int | None = None,
    *,
    candidates_per_ticket: int = 320,
) -> list[Ticket]:
    """Greedy combinatorial design for multiple distinct standard entries.

    The objective prioritises new 4-, 3-, then 2-number subsets, followed by low
    ticket overlap and balanced number usage. This cannot improve an individual
    six-number combination's draw probability; it reduces portfolio redundancy.
    """
    _validate_count(count)
    if candidates_per_ticket < 20:
        raise ValueError("candidates_per_ticket must be at least 20")
    rng = _rng(seed)
    tickets: list[Ticket] = []
    seen: set[Ticket] = set()
    usage = Counter({number: 0 for number in range(1, BALL_COUNT + 1)})
    covered: dict[int, set[tuple[int, ...]]] = {2: set(), 3: set(), 4: set()}

    for _ in range(count):
        best_ticket: Ticket | None = None
        best_score: tuple[float, ...] | None = None
        for _candidate in range(candidates_per_ticket):
            candidate = _random_ticket(rng)
            if candidate in seen:
                continue
            new4, new3, new2, max_overlap, usage_cost, _overlaps = _candidate_structure(
                candidate, tickets, usage, covered
            )
            score = (new4, new3, new2, -max_overlap, -usage_cost, rng.random())
            if best_score is None or score > best_score:
                best_score = score
                best_ticket = candidate

        if best_ticket is None:
            raise RuntimeError("unable to generate a unique coverage ticket")
        tickets.append(best_ticket)
        seen.add(best_ticket)
        usage.update(best_ticket)
        for size in covered:
            covered[size].update(combinations(best_ticket, size))

    return tickets


def generate_probability_bound_tickets(
    count: int,
    seed: str | int | None = None,
    *,
    event_threshold: int,
    candidates_per_ticket: int = 320,
) -> list[Ticket]:
    """Greedily optimise an exact second-order union-probability lower bound.

    Every candidate ticket has the same single-ticket event probability. Maximising
    the Bonferroni lower bound therefore means minimising the exact sum of its pairwise
    event intersections with tickets already selected. Structural coverage then acts
    only as a tie-breaker.

    threshold=3 targets the rigorous lower bound for winning any prize.
    threshold=4 targets Division 4-or-better and can achieve an exact global optimum
    whenever all >=4-main ticket events become pairwise disjoint.
    """
    _validate_count(count)
    if event_threshold < 3 or event_threshold > MAIN_COUNT:
        raise ValueError("event_threshold must be between 3 and 6")
    if candidates_per_ticket < 20:
        raise ValueError("candidates_per_ticket must be at least 20")

    rng = _rng(seed)
    tickets: list[Ticket] = []
    seen: set[Ticket] = set()
    usage = Counter({number: 0 for number in range(1, BALL_COUNT + 1)})
    covered: dict[int, set[tuple[int, ...]]] = {2: set(), 3: set(), 4: set()}

    for _ in range(count):
        best_ticket: Ticket | None = None
        best_score: tuple[float, ...] | None = None
        for _candidate in range(candidates_per_ticket):
            candidate = _random_ticket(rng)
            if candidate in seen:
                continue
            new4, new3, new2, max_overlap, usage_cost, overlaps = _candidate_structure(
                candidate, tickets, usage, covered
            )
            target_pair_cost = sum(
                pair_event_intersection_count(overlap, event_threshold)
                for overlap in overlaps
            )
            any_prize_pair_cost = sum(
                pair_event_intersection_count(overlap, 3) for overlap in overlaps
            )
            score = (
                -target_pair_cost,
                -any_prize_pair_cost,
                new4,
                new3,
                new2,
                -max_overlap,
                -usage_cost,
                rng.random(),
            )
            if best_score is None or score > best_score:
                best_score = score
                best_ticket = candidate

        if best_ticket is None:
            raise RuntimeError("unable to generate a unique probability-bound ticket")
        tickets.append(best_ticket)
        seen.add(best_ticket)
        usage.update(best_ticket)
        for size in covered:
            covered[size].update(combinations(best_ticket, size))

    return tickets


def generate_any_prize_bound_tickets(
    count: int,
    seed: str | int | None = None,
    *,
    candidates_per_ticket: int = 320,
) -> list[Ticket]:
    return generate_probability_bound_tickets(
        count,
        seed,
        event_threshold=3,
        candidates_per_ticket=candidates_per_ticket,
    )


def generate_division4_bound_tickets(
    count: int,
    seed: str | int | None = None,
    *,
    candidates_per_ticket: int = 320,
) -> list[Ticket]:
    return generate_probability_bound_tickets(
        count,
        seed,
        event_threshold=4,
        candidates_per_ticket=candidates_per_ticket,
    )


def ticket_metrics(tickets: Iterable[Ticket]) -> dict[str, float | int | dict]:
    ticket_list = list(tickets)
    if not ticket_list:
        return {
            "ticketCount": 0,
            "uniqueNumbers": 0,
            "maxPairwiseOverlap": 0,
            "averagePairwiseOverlap": 0.0,
            "usageSpread": 0,
            "divisionOneProbability": 0.0,
            "pairCoverage": subset_coverage([], 2),
            "tripleCoverage": subset_coverage([], 3),
            "quadrupleCoverage": subset_coverage([], 4),
            "probabilityCertificates": {
                "anyPrize": portfolio_probability_certificate([], threshold=3),
                "division4OrBetter": portfolio_probability_certificate([], threshold=4),
            },
        }

    usage = Counter(number for ticket in ticket_list for number in ticket)
    overlaps = [len(set(a) & set(b)) for a, b in combinations(ticket_list, 2)]
    all_usage = [usage[number] for number in range(1, BALL_COUNT + 1)]
    return {
        "ticketCount": len(ticket_list),
        "uniqueNumbers": len(usage),
        "maxPairwiseOverlap": max(overlaps, default=0),
        "averagePairwiseOverlap": round(sum(overlaps) / len(overlaps), 4) if overlaps else 0.0,
        "usageSpread": max(all_usage) - min(all_usage),
        "divisionOneProbability": division_one_probability(len(ticket_list)),
        "pairCoverage": subset_coverage(ticket_list, 2),
        "tripleCoverage": subset_coverage(ticket_list, 3),
        "quadrupleCoverage": subset_coverage(ticket_list, 4),
        "probabilityCertificates": {
            "anyPrize": portfolio_probability_certificate(ticket_list, threshold=3),
            "division4OrBetter": portfolio_probability_certificate(ticket_list, threshold=4),
        },
    }


def _validate_count(count: int) -> None:
    if count < 1:
        raise ValueError("count must be at least 1")
    if count > 5000:
        raise ValueError("count is capped at 5000 for practical generation")
