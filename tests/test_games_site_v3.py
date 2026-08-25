import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class GamesSiteTests(unittest.TestCase):
    def test_games_page_and_assets_exist(self):
        for relative in (
            "games.html",
            "assets/ui.js",
            "assets/games.js",
            "assets/game_catalog.json",
        ):
            self.assertTrue((ROOT / relative).exists(), relative)

    def test_games_page_references_library_assets_and_calculators(self):
        page = (ROOT / "games.html").read_text(encoding="utf-8")
        self.assertIn("bulma@1.0.4/css/bulma.min.css", page)
        self.assertIn("lucide@1.33.0/dist/umd/lucide.js", page)
        self.assertIn("assets/ui.js", page)
        self.assertIn("assets/games.js", page)
        self.assertNotIn("assets/games.css", page)
        self.assertIn('id="game-grid"', page)
        self.assertIn('id="keno-spot"', page)
        self.assertIn('id="cash3-digits"', page)
        self.assertIn('id="sfl-draws"', page)

    def test_primary_navigation_exposes_all_research_surfaces(self):
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        games = (ROOT / "games.html").read_text(encoding="utf-8")
        benchmark = (ROOT / "benchmark.html").read_text(encoding="utf-8")
        for page in (index, games, benchmark):
            self.assertIn('href="index.html"', page)
            self.assertIn('href="games.html"', page)
            self.assertIn('href="benchmark.html"', page)
            self.assertIn("navbar", page)
        self.assertIn('href="index.html" aria-current="page"', index)
        self.assertIn('href="games.html" aria-current="page"', games)
        self.assertIn('href="benchmark.html" aria-current="page"', benchmark)

    def test_browser_catalog_is_generated_not_hard_coded(self):
        script = (ROOT / "assets/games.js").read_text(encoding="utf-8")
        payload = json.loads((ROOT / "assets/game_catalog.json").read_text(encoding="utf-8"))
        slugs = {row["slug"] for row in payload["games"]}
        self.assertIn("assets/game_catalog.json", script)
        self.assertNotIn("const games = [", script)
        for slug in (
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
            "millionaire-medley",
            "cash-3",
            "mater-prize-home",
            "yourtown-prize-home",
        ):
            self.assertIn(slug, slugs)

    def test_catalog_public_guardrails(self):
        payload = json.loads((ROOT / "assets/game_catalog.json").read_text(encoding="utf-8"))
        rows = {row["slug"]: row for row in payload["games"]}
        self.assertEqual(payload["schemaVersion"], 1)
        self.assertEqual(payload["checkedOn"], "2026-08-23")
        self.assertEqual(rows["powerball"]["computedTopOdds"], 134_490_400.0)
        self.assertIsNone(rows["weekday-windfall"]["officialAnyOdds"])
        self.assertIsNone(rows["lucky-lotteries-super"]["officialAnyOdds"])
        self.assertIsNone(rows["yourtown-prize-home"]["computedTopOdds"])
        self.assertEqual(
            rows["mater-prize-home"]["raffleSnapshot"]["maximumEntries"],
            22_805_334,
        )

    def test_pwa_exposes_games_lab_and_library_dependencies(self):
        manifest = json.loads((ROOT / "assets/site.webmanifest").read_text(encoding="utf-8"))
        shortcut_urls = {shortcut["url"] for shortcut in manifest["shortcuts"]}
        self.assertIn("../games.html", shortcut_urls)

        worker = (ROOT / "service-worker.js").read_text(encoding="utf-8")
        self.assertIn("./games.html", worker)
        self.assertIn("./assets/ui.js", worker)
        self.assertIn("./assets/games.js", worker)
        self.assertIn("./assets/game_catalog.json", worker)
        self.assertIn("bulma@1.0.4/css/bulma.min.css", worker)
        self.assertIn("lucide@1.33.0/dist/umd/lucide.js", worker)
        self.assertIn("australian-lottery-lab-bulma-v2", worker)


if __name__ == "__main__":
    unittest.main()
