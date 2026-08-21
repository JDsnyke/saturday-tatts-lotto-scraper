from __future__ import annotations

import hashlib
import random
from collections import Counter
from collections.abc import Iterable
from itertools import combinations

from .domain import BALL_COUNT, MAIN_COUNT
from .probability import division_one_probability

Ticket = tuple[int, ...]


def _rng(seed: str | int | None = None) -> random.Random:
    if seed is None:
        return random.SystemRandom()
    if isinstance(seed, str):
        digest = hashlib.sha256(seed.encode("utf-8")).digest()
        seed = int.from_bytes(digest[:16], "big")
    return random.Random(seed)


def generate_random_tickets(count: int, seed: str | int | None = None) -> list[Ticket]:
    _validate_count(count)
    rng = _rng(seed)
    seen: set[Ticket] = set()
    tickets: list[Ticket] = []
    population = list(range(1, BALL_COUNT + 1))
    while len(tickets) < count:
        ticket = tuple(sorted(rng.sample(population, MAIN_COUNT)))
        if ticket not in seen:
            seen.add(ticket)
            tickets.append(ticket)
    return tickets


def generate_coverage_tickets(count: int, seed: str | int | None = None) -> list[Ticket]:
    """Generate tickets with balanced number usage and low repeated-pair overlap.

    This does *not* increase the probability of any individual combination. It is useful
    only when constructing multiple distinct entries because it reduces redundant coverage.
    """
    _validate_count(count)
    rng = _rng(seed)
    usage = Counter({number: 0 for number in range(1, BALL_COUNT + 1)})
    pair_usage: Counter[tuple[int, int]] = Counter()
    tickets: list[Ticket] = []
    seen: set[Ticket] = set()

    for _ in range(count):
        for _attempt in range(100):
            chosen: list[int] = []
            while len(chosen) < MAIN_COUNT:
                candidates = [number for number in range(1, BALL_COUNT + 1) if number not in chosen]
                rng.shuffle(candidates)

                def score(number: int) -> tuple[float, float, float]:
                    repeated_pairs = sum(pair_usage[tuple(sorted((number, other)))] for other in chosen)
                    shared_with_existing = sum(
                        1
                        for ticket in tickets
                        if number in ticket and any(other in ticket for other in chosen)
                    )
                    return (usage[number], repeated_pairs, shared_with_existing + rng.random() * 0.01)

                chosen.append(min(candidates, key=score))

            ticket = tuple(sorted(chosen))
            if ticket not in seen:
                break
            rng.random()
        else:
            raise RuntimeError("unable to generate a unique ticket set")

        seen.add(ticket)
        tickets.append(ticket)
        usage.update(ticket)
        pair_usage.update(tuple(sorted(pair)) for pair in combinations(ticket, 2))

    return tickets


def ticket_metrics(tickets: Iterable[Ticket]) -> dict[str, float | int]:
    ticket_list = list(tickets)
    if not ticket_list:
        return {
            "ticketCount": 0,
            "uniqueNumbers": 0,
            "maxPairwiseOverlap": 0,
            "averagePairwiseOverlap": 0.0,
            "usageSpread": 0,
            "divisionOneProbability": 0.0,
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
    }


def _validate_count(count: int) -> None:
    if count < 1:
        raise ValueError("count must be at least 1")
    if count > 5000:
        raise ValueError("count is capped at 5000 for practical generation")
