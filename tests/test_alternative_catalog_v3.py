import unittest

from lotto_lab.alternative_catalog import (
    ALTERNATIVE_GAMES,
    ALTERNATIVE_SNAPSHOTS,
    alternative_snapshot,
)
from lotto_lab.game_cli import catalog_payload


class AlternativeCatalogTests(unittest.TestCase):
    def test_expected_verified_alternative_families_exist(self):
        expected = {
            "yourtown-prize-home",
            "mater-prize-home",
            "mater-cars-for-cancer",
            "dream-home-art-union",
            "endeavour-prize-home",
            "endeavour-pay-day",
        }
        self.assertTrue(expected.issubset(ALTERNATIVE_GAMES))
        self.assertTrue(expected.issubset(ALTERNATIVE_SNAPSHOTS))

    def test_alternative_games_are_variable_raffles_not_fake_fixed_odds(self):
        for game in ALTERNATIVE_GAMES.values():
            self.assertEqual(game.mechanic, "variable-raffle", game.slug)
            self.assertIsNone(game.official_top_odds, game.slug)
            self.assertIsNone(game.official_any_odds, game.slug)
            self.assertTrue(game.sources, game.slug)
            for source in game.sources:
                self.assertEqual(source.checked_on, "2026-08-23")
                self.assertTrue(source.url.startswith("https://"))

    def test_yourtown_capacity_is_not_presented_as_exact_odds(self):
        snapshot = alternative_snapshot("yourtown-prize-home")
        self.assertEqual(snapshot["maximum_entries"], 500_000)
        self.assertIn("tickets sold", snapshot["probability_note"])
        row = self._catalog_row("yourtown-prize-home")
        self.assertIsNone(row["computedTopOdds"])
        self.assertIsNone(row["officialTopOdds"])

    def test_mater_prize_home_327_snapshot_matches_current_terms(self):
        snapshot = alternative_snapshot("mater-prize-home")
        self.assertEqual(snapshot["draw_id"], "327")
        self.assertEqual(snapshot["close_date"], "2026-10-20")
        self.assertEqual(snapshot["draw_date"], "2026-10-23")
        self.assertEqual(snapshot["ticket_price_from"], 2.0)
        self.assertEqual(snapshot["minimum_possible_entries"], 13_455_147)
        self.assertEqual(snapshot["maximum_entries"], 22_805_334)
        self.assertEqual(snapshot["first_prize_value"], 5_382_059.0)

    def test_mater_cars_130_snapshot_matches_current_terms(self):
        snapshot = alternative_snapshot("mater-cars-for-cancer")
        self.assertEqual(snapshot["draw_id"], "130")
        self.assertEqual(snapshot["close_date"], "2026-09-13")
        self.assertEqual(snapshot["draw_date"], "2026-09-16")
        self.assertEqual(snapshot["ticket_price_from"], 30.0)
        self.assertEqual(snapshot["maximum_entries"], 85_117)
        self.assertEqual(snapshot["first_prize_value"], 510_707.0)

    def test_endeavour_prize_home_468_is_marked_drawn_and_sold_out(self):
        snapshot = alternative_snapshot("endeavour-prize-home")
        self.assertEqual(snapshot["draw_id"], "468")
        self.assertEqual(snapshot["status"], "sold out / drawn")
        self.assertEqual(snapshot["draw_date"], "2026-08-20")
        self.assertEqual(snapshot["ticket_price_from"], 10.0)
        self.assertEqual(snapshot["first_prize_value"], 3_700_000.0)

    def test_endeavour_payday_does_not_invent_unverified_close_date(self):
        snapshot = alternative_snapshot("endeavour-pay-day")
        self.assertEqual(snapshot["draw_id"], "221")
        self.assertEqual(snapshot["draw_date"], "2026-10-08")
        self.assertIsNone(snapshot["close_date"])
        self.assertEqual(snapshot["ticket_price_from"], 5.0)
        self.assertEqual(snapshot["maximum_entries"], 200_000)
        self.assertEqual(snapshot["first_prize_value"], 200_000.0)

    def test_public_catalog_masks_unverified_aggregate_any_prize_odds(self):
        rows = {row["slug"]: row for row in catalog_payload()["games"]}
        for slug in (
            "weekday-windfall",
            "lotto-strike",
            "lucky-lotteries-super",
            "lucky-lotteries-mega",
        ):
            self.assertIsNone(rows[slug]["officialAnyOdds"], slug)
            self.assertIsNone(rows[slug]["exactAnyPrizeOdds"], slug)

    def test_catalog_payload_includes_all_alternatives_and_guardrail(self):
        payload = catalog_payload()
        slugs = {row["slug"] for row in payload["games"]}
        self.assertTrue(set(ALTERNATIVE_GAMES).issubset(slugs))
        self.assertIn("not automatically", payload["guardrails"]["variableRaffles"])

    def _catalog_row(self, slug: str) -> dict:
        return next(row for row in catalog_payload()["games"] if row["slug"] == slug)


if __name__ == "__main__":
    unittest.main()
