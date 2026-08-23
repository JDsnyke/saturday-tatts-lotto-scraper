import unittest
from fractions import Fraction

from lotto_lab.game_catalog import GAMES, get_game
from lotto_lab.game_probability import (
    cash3_any_order_probability,
    computed_top_prize_probability,
    cumulative_probability,
    exact_any_prize_probability,
    game_odds_summary,
    keno_all_spot_probability,
    keno_match_distribution,
    one_pool_match_distribution,
    two_pool_match_distribution,
)


class GameCatalogTests(unittest.TestCase):
    def test_catalog_contains_distinct_the_lott_and_lotterywest_mechanics(self):
        expected = {
            "saturday-lotto",
            "weekday-windfall",
            "oz-lotto",
            "powerball",
            "set-for-life",
            "super-66",
            "lotto-strike",
            "lucky-lotteries-super",
            "lucky-lotteries-mega",
            "keno-sa",
            "instant-scratch-its",
            "play-for-purpose",
            "millionaire-medley",
            "cash-3",
            "scratch-n-win",
        }
        self.assertTrue(expected.issubset(GAMES))
        self.assertEqual(get_game("cash-3").operator, "Lotterywest")
        self.assertEqual(get_game("powerball").mechanic, "two-pool")
        self.assertEqual(get_game("lotto-strike").jurisdictions, ("NSW", "ACT"))
        self.assertEqual(get_game("keno-sa").jurisdictions, ("SA",))

    def test_all_catalog_entries_have_current_source_provenance(self):
        for game in GAMES.values():
            self.assertTrue(game.sources, game.slug)
            for source in game.sources:
                self.assertTrue(source.url.startswith("https://"), game.slug)
                self.assertEqual(source.checked_on, "2026-08-23")

    def test_computed_top_prize_denominators_match_official_odds(self):
        expected = {
            "saturday-lotto": 8_145_060,
            "weekday-windfall": 8_145_060,
            "oz-lotto": 62_891_499,
            "powerball": 134_490_400,
            "set-for-life": 38_320_568,
            "super-66": 1_000_000,
            "lotto-strike": 3_575_880,
            "millionaire-medley": 8_145_060,
            "cash-3": 1_000,
        }
        for slug, denominator in expected.items():
            game = get_game(slug)
            probability = computed_top_prize_probability(game)
            self.assertEqual(probability, Fraction(1, denominator), slug)
            self.assertEqual(game.official_top_odds, denominator, slug)
            self.assertTrue(game_odds_summary(game)["computedTopMatchesOfficial"], slug)

    def test_variable_and_raffle_games_do_not_invent_computed_top_odds(self):
        for slug in (
            "lucky-lotteries-super",
            "lucky-lotteries-mega",
            "instant-scratch-its",
            "play-for-purpose",
            "keno-sa",
            "scratch-n-win",
        ):
            self.assertIsNone(computed_top_prize_probability(get_game(slug)), slug)

    def test_one_pool_distributions_sum_to_one(self):
        for slug in ("saturday-lotto", "weekday-windfall", "oz-lotto", "set-for-life", "millionaire-medley"):
            distribution = one_pool_match_distribution(get_game(slug))
            self.assertEqual(sum(distribution.values(), Fraction()), 1, slug)

    def test_powerball_distribution_sums_to_one(self):
        distribution = two_pool_match_distribution(get_game("powerball"))
        self.assertEqual(sum(distribution.values(), Fraction()), 1)
        self.assertEqual(distribution[(7, True)], Fraction(1, 134_490_400))

    def test_exact_any_prize_odds_track_official_rounded_values(self):
        expected_rounded = {
            "saturday-lotto": 42,
            "oz-lotto": 51,
            "powerball": 44,
            "set-for-life": 51,
            "millionaire-medley": 86,
        }
        for slug, official_odds in expected_rounded.items():
            probability = exact_any_prize_probability(get_game(slug))
            self.assertIsNotNone(probability)
            exact_odds = float(1 / probability)
            self.assertLess(abs(exact_odds - official_odds), 1.0, slug)

    def test_unverified_weekday_lower_divisions_are_not_inferred(self):
        summary = game_odds_summary("weekday-windfall")
        self.assertIsNone(summary["exactAnyPrize"])
        self.assertEqual(summary["official_any_odds"], 86.0)

    def test_set_for_life_standard_purchase_cumulative_top_probability(self):
        game = get_game("set-for-life")
        single = Fraction(1, 38_320_568)
        expected = cumulative_probability(single, 7)
        summary = game_odds_summary(game)
        self.assertEqual(game.draws_per_purchase, 7)
        self.assertEqual(
            Fraction(
                summary["topPrizeAcrossStandardPurchase"]["numerator"],
                summary["topPrizeAcrossStandardPurchase"]["denominator"],
            ),
            expected,
        )
        self.assertGreater(expected, single)

    def test_keno_spot_distributions_are_exact(self):
        for spot in range(1, 11):
            distribution = keno_match_distribution(spot)
            self.assertEqual(sum(distribution.values(), Fraction()), 1)
            self.assertEqual(distribution[spot], keno_all_spot_probability(spot))
        self.assertEqual(keno_all_spot_probability(10), Fraction(17, 151_499_090))

    def test_cash3_any_order_handles_multiset_permutations(self):
        self.assertEqual(cash3_any_order_probability((1, 1, 1)), Fraction(1, 1000))
        self.assertEqual(cash3_any_order_probability((2, 2, 3)), Fraction(3, 1000))
        self.assertEqual(cash3_any_order_probability((1, 2, 3)), Fraction(6, 1000))
        self.assertAlmostEqual(float(1 / cash3_any_order_probability((2, 2, 3))), 333.3333333)
        self.assertAlmostEqual(float(1 / cash3_any_order_probability((1, 2, 3))), 166.6666667)


if __name__ == "__main__":
    unittest.main()
