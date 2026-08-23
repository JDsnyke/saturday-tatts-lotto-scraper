import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class GameSiteTests(unittest.TestCase):
    def test_games_lab_assets_and_generated_catalog_exist(self):
        for path in (
            "games.html",
            "assets/games.css",
            "assets/games.js",
            "assets/game_catalog.json",
        ):
            self.assertTrue((ROOT / path).is_file(), path)

    def test_games_page_uses_catalog_loader_and_calculators(self):
        html = (ROOT / "games.html").read_text(encoding="utf-8")
        javascript = (ROOT / "assets/games.js").read_text(encoding="utf-8")
        self.assertIn('id="game-grid"', html)
        self.assertIn('id="keno-spot"', html)
        self.assertIn('id="cash3-digits"', html)
        self.assertIn("assets/game_catalog.json", javascript)
        self.assertNotIn("const games = [", javascript)

    def test_tracked_catalog_has_expected_public_guardrails(self):
        payload = json.loads((ROOT / "assets/game_catalog.json").read_text(encoding="utf-8"))
        rows = {row["slug"]: row for row in payload["games"]}
        self.assertEqual(payload["schemaVersion"], 1)
        self.assertEqual(payload["checkedOn"], "2026-08-23")
        self.assertGreaterEqual(len(rows), 20)
        self.assertEqual(rows["powerball"]["computedTopOdds"], 134_490_400.0)
        self.assertIsNone(rows["weekday-windfall"]["officialAnyOdds"])
        self.assertIsNone(rows["lucky-lotteries-super"]["officialAnyOdds"])
        self.assertIsNone(rows["yourtown-prize-home"]["computedTopOdds"])
        self.assertEqual(
            rows["mater-prize-home"]["raffleSnapshot"]["maximumEntries"],
            22_805_334,
        )

    def test_service_worker_caches_catalog_and_games_page(self):
        worker = (ROOT / "service-worker.js").read_text(encoding="utf-8")
        self.assertIn("australian-lottery-lab-v3-0-0", worker)
        self.assertIn("./games.html", worker)
        self.assertIn("./assets/game_catalog.json", worker)


if __name__ == "__main__":
    unittest.main()
