from __future__ import annotations

from fractions import Fraction
from math import comb, perm
from typing import Iterable

from .game_catalog import GameDefinition, PrizePattern, get_game


def _safe_comb(n: int, k: int) -> int:
    if n < 0 or k < 0 or k > n:
        return 0
    return comb(n, k)


def odds_from_fraction(probability: Fraction) -> float | None:
    if probability <= 0:
        return None
    return float(1 / probability)


def cumulative_probability(probability: Fraction, draws: int) -> Fraction:
    if draws < 0:
        raise ValueError("draws must be non-negative")
    return 1 - (1 - probability) ** draws


def one_pool_match_distribution(game: GameDefinition) -> dict[tuple[int, int], Fraction]:
    if game.mechanic != "one-pool":
        raise ValueError(f"{game.slug} is not a one-pool game")
    if game.pool_size is None or game.ticket_pick is None or game.winning_count is None:
        raise ValueError(f"{game.slug} has an incomplete one-pool definition")

    pool = game.pool_size
    pick = game.ticket_pick
    winning = game.winning_count
    supplementary = game.supplementary_count
    outside = pool - winning - supplementary
    denominator = comb(pool, pick)
    distribution: dict[tuple[int, int], Fraction] = {}

    for main_matches in range(0, min(pick, winning) + 1):
        for supplementary_matches in range(0, min(pick - main_matches, supplementary) + 1):
            outside_picks = pick - main_matches - supplementary_matches
            ways = (
                _safe_comb(winning, main_matches)
                * _safe_comb(supplementary, supplementary_matches)
                * _safe_comb(outside, outside_picks)
            )
            if ways:
                distribution[(main_matches, supplementary_matches)] = Fraction(ways, denominator)

    if sum(distribution.values(), Fraction()) != 1:
        raise AssertionError(f"{game.slug} match distribution does not sum to 1")
    return distribution


def two_pool_match_distribution(game: GameDefinition) -> dict[tuple[int, bool], Fraction]:
    if game.mechanic != "two-pool":
        raise ValueError(f"{game.slug} is not a two-pool game")
    if (
        game.pool_size is None
        or game.ticket_pick is None
        or game.winning_count is None
        or game.secondary_pool_size is None
        or game.secondary_ticket_pick != 1
    ):
        raise ValueError(f"{game.slug} has an incomplete two-pool definition")

    main_denominator = comb(game.pool_size, game.ticket_pick)
    secondary_denominator = game.secondary_pool_size
    distribution: dict[tuple[int, bool], Fraction] = {}

    for main_matches in range(0, min(game.ticket_pick, game.winning_count) + 1):
        main_ways = _safe_comb(game.winning_count, main_matches) * _safe_comb(
            game.pool_size - game.winning_count,
            game.ticket_pick - main_matches,
        )
        main_probability = Fraction(main_ways, main_denominator)
        if not main_probability:
            continue
        distribution[(main_matches, True)] = main_probability * Fraction(1, secondary_denominator)
        distribution[(main_matches, False)] = main_probability * Fraction(
            secondary_denominator - 1,
            secondary_denominator,
        )

    if sum(distribution.values(), Fraction()) != 1:
        raise AssertionError(f"{game.slug} two-pool distribution does not sum to 1")
    return distribution


def _pattern_matches_one_pool(pattern: PrizePattern, main_matches: int, supp_matches: int) -> bool:
    if main_matches not in pattern.main_matches:
        return False
    if pattern.supplementary_matches is not None and supp_matches not in pattern.supplementary_matches:
        return False
    return True


def _pattern_matches_two_pool(pattern: PrizePattern, main_matches: int, secondary_match: bool) -> bool:
    if main_matches not in pattern.main_matches:
        return False
    if pattern.secondary_match is not None and secondary_match is not pattern.secondary_match:
        return False
    return True


def one_pool_prize_probabilities(game: GameDefinition) -> dict[str, Fraction]:
    if not game.prize_patterns:
        raise ValueError(f"{game.slug} does not have verified prize patterns")
    distribution = one_pool_match_distribution(game)
    probabilities = {pattern.label: Fraction() for pattern in game.prize_patterns}

    for (main_matches, supp_matches), probability in distribution.items():
        matches = [
            pattern
            for pattern in game.prize_patterns
            if _pattern_matches_one_pool(pattern, main_matches, supp_matches)
        ]
        if len(matches) > 1:
            labels = ", ".join(pattern.label for pattern in matches)
            raise AssertionError(f"overlapping prize patterns for {game.slug}: {labels}")
        if matches:
            probabilities[matches[0].label] += probability
    return probabilities


def two_pool_prize_probabilities(game: GameDefinition) -> dict[str, Fraction]:
    if not game.prize_patterns:
        raise ValueError(f"{game.slug} does not have verified prize patterns")
    distribution = two_pool_match_distribution(game)
    probabilities = {pattern.label: Fraction() for pattern in game.prize_patterns}

    for (main_matches, secondary_match), probability in distribution.items():
        matches = [
            pattern
            for pattern in game.prize_patterns
            if _pattern_matches_two_pool(pattern, main_matches, secondary_match)
        ]
        if len(matches) > 1:
            labels = ", ".join(pattern.label for pattern in matches)
            raise AssertionError(f"overlapping prize patterns for {game.slug}: {labels}")
        if matches:
            probabilities[matches[0].label] += probability
    return probabilities


def exact_any_prize_probability(game: GameDefinition) -> Fraction | None:
    if not game.prize_patterns:
        return None
    if game.mechanic == "one-pool":
        return sum(one_pool_prize_probabilities(game).values(), Fraction())
    if game.mechanic == "two-pool":
        return sum(two_pool_prize_probabilities(game).values(), Fraction())
    return None


def computed_top_prize_probability(game: GameDefinition) -> Fraction | None:
    if game.mechanic == "one-pool":
        if game.pool_size is None or game.ticket_pick is None or game.winning_count != game.ticket_pick:
            return None
        return Fraction(1, comb(game.pool_size, game.ticket_pick))

    if game.mechanic == "two-pool":
        if (
            game.pool_size is None
            or game.ticket_pick is None
            or game.winning_count != game.ticket_pick
            or game.secondary_pool_size is None
            or game.secondary_ticket_pick != 1
        ):
            return None
        return Fraction(1, comb(game.pool_size, game.ticket_pick) * game.secondary_pool_size)

    if game.mechanic == "ordered-digits":
        if game.ordered_positions is None or game.radix is None:
            return None
        return Fraction(1, game.radix**game.ordered_positions)

    if game.mechanic == "ordered-without-replacement":
        if game.pool_size is None or game.ordered_positions is None:
            return None
        return Fraction(1, perm(game.pool_size, game.ordered_positions))

    return None


def keno_match_distribution(spot_size: int, *, pool_size: int = 80, draw_count: int = 20) -> dict[int, Fraction]:
    if spot_size < 1 or spot_size > pool_size:
        raise ValueError("spot_size must be between 1 and the pool size")
    if draw_count < 0 or draw_count > pool_size:
        raise ValueError("draw_count must be between 0 and the pool size")

    denominator = comb(pool_size, draw_count)
    distribution: dict[int, Fraction] = {}
    for matches in range(0, min(spot_size, draw_count) + 1):
        ways = _safe_comb(spot_size, matches) * _safe_comb(
            pool_size - spot_size,
            draw_count - matches,
        )
        if ways:
            distribution[matches] = Fraction(ways, denominator)

    if sum(distribution.values(), Fraction()) != 1:
        raise AssertionError("Keno match distribution does not sum to 1")
    return distribution


def keno_all_spot_probability(spot_size: int) -> Fraction:
    return keno_match_distribution(spot_size)[spot_size]


def cash3_any_order_probability(digits: Iterable[int]) -> Fraction:
    values = tuple(digits)
    if len(values) != 3 or any(digit < 0 or digit > 9 for digit in values):
        raise ValueError("Cash 3 requires exactly three digits from 0 to 9")
    counts = sorted((values.count(value) for value in set(values)), reverse=True)
    if counts == [3]:
        permutations = 1
    elif counts == [2, 1]:
        permutations = 3
    else:
        permutations = 6
    return Fraction(permutations, 1000)


def _fraction_payload(probability: Fraction | None) -> dict | None:
    if probability is None:
        return None
    return {
        "numerator": probability.numerator,
        "denominator": probability.denominator,
        "probability": float(probability),
        "odds": odds_from_fraction(probability),
    }


def game_odds_summary(game: GameDefinition | str) -> dict:
    if isinstance(game, str):
        game = get_game(game)

    computed_top = computed_top_prize_probability(game)
    exact_any = exact_any_prize_probability(game)
    payload = game.to_dict()
    payload["computedTopPrize"] = _fraction_payload(computed_top)
    payload["exactAnyPrize"] = _fraction_payload(exact_any)
    payload["officialTopProbability"] = (
        None if game.official_top_odds is None else 1 / game.official_top_odds
    )
    payload["officialAnyProbability"] = (
        None if game.official_any_odds is None else 1 / game.official_any_odds
    )
    payload["computedTopMatchesOfficial"] = (
        None
        if computed_top is None or game.official_top_odds is None
        else computed_top.denominator == game.official_top_odds and computed_top.numerator == 1
    )

    if computed_top is not None and game.draws_per_purchase > 1:
        payload["topPrizeAcrossStandardPurchase"] = _fraction_payload(
            cumulative_probability(computed_top, game.draws_per_purchase)
        )
    else:
        payload["topPrizeAcrossStandardPurchase"] = None

    if exact_any is not None and game.draws_per_purchase > 1:
        payload["anyPrizeAcrossStandardPurchase"] = _fraction_payload(
            cumulative_probability(exact_any, game.draws_per_purchase)
        )
    else:
        payload["anyPrizeAcrossStandardPurchase"] = None

    return payload
