from __future__ import annotations

import hashlib
import random
from statistics import pvariance

from .tickets import Ticket, generate_random_tickets


def _research_rng(seed: str | int | None) -> random.Random:
    if seed is None:
        return random.SystemRandom()
    if isinstance(seed, str):
        digest = hashlib.sha256(seed.encode("utf-8")).digest()
        seed = int.from_bytes(digest[:16], "big")
    return random.Random(seed)


def crowding_features(ticket: Ticket) -> dict[str, float | int | bool]:
    """Evidence-informed human-choice features; not Australia-calibrated probabilities."""
    ordered = sorted(ticket)
    gaps = [b - a for a, b in zip(ordered, ordered[1:])]
    consecutive_pairs = sum(gap == 1 for gap in gaps)
    birthday_numbers = sum(number <= 31 for number in ordered)
    evenly_spaced = len(gaps) >= 2 and pvariance(gaps) <= 2.0
    return {
        "birthdayNumbers": birthday_numbers,
        "containsSeven": 7 in ordered,
        "consecutivePairs": consecutive_pairs,
        "evenlySpaced": evenly_spaced,
    }


def crowding_penalty(ticket: Ticket) -> float:
    features = crowding_features(ticket)
    penalty = float(features["birthdayNumbers"]) * 1.0
    penalty += 1.25 if features["containsSeven"] else 0.0
    penalty += float(features["consecutivePairs"]) * 1.5
    penalty += 1.5 if features["evenlySpaced"] else 0.0
    if features["birthdayNumbers"] == 6:
        penalty += 2.0
    return penalty


def generate_anti_crowding_tickets(
    count: int,
    seed: str | int | None = None,
    *,
    candidate_pool: int = 1200,
) -> list[Ticket]:
    """Select low-crowding candidates without changing draw probability.

    This is an experimental conditional-payout heuristic: academic lottery data
    show player choices cluster around birthdays, 7, sequences and aesthetic/
    evenly spaced patterns. It is not calibrated to Australian Saturday Lotto.
    """
    if count < 1:
        raise ValueError("count must be at least 1")
    rng = _research_rng(seed)
    pool = generate_random_tickets(max(candidate_pool, count * 20), seed=rng.randrange(2**63))
    ranked = sorted(pool, key=lambda ticket: (crowding_penalty(ticket), rng.random()))
    return ranked[:count]
