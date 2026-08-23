import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class GamesSiteTests(unittest.TestCase):
    def test_games_page_and_assets_exist(self):
        for relative in ("games.html", "assets/games.css", "assets/games.js"):
            self.assertTrue((ROOT / relative).exists(), relative)

    def test_games_page_references_assets_and_calculators(self):
        page = (ROOT / "games.html").read_text(encoding="utf-8")
        self.assertIn("assets/app.css", page)
        self.assertIn("assets/games.css", page)
        self.assertIn("assets/games.js", page)
        self.assertIn('id="game-grid"', page)
        self.assertIn('id="keno-spot"', page)
        self.assertIn('id="cash3-digits"', page)
        self.assertIn('id="sfl-draws"', page)

    def test_browser_catalog_contains_core_distinct_options(self):
        script = (ROOT / "assets/games.js").read_text(encoding="utf-8")
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
        ):
            self.assertIn(slug, script)

    def test_pwa_exposes_games_lab(self):
        manifest = json.loads((ROOT / "assets/site.webmanifest").read_text(encoding="utf-8"))
        shortcut_urls = {shortcut["url"] for shortcut in manifest["shortcuts"]}
        self.assertIn("../games.html", shortcut_urls)

        worker = (ROOT / "service-worker.js").read_text(encoding="utf-8")
        self.assertIn("./games.html", worker)
        self.assertIn("./assets/games.css", worker)
        self.assertIn("./assets/games.js", worker)
        self.assertIn("australian-lottery-lab-v3-games", worker)


if __name__ == "__main__":
    unittest.main()
