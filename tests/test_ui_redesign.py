import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index.html", "games.html", "benchmark.html")


class UiRedesignTests(unittest.TestCase):
    def test_no_custom_design_stylesheets_remain(self):
        for name in ("assets/app.css", "assets/games.css", "assets/benchmark.css"):
            self.assertFalse((ROOT / name).exists(), name)

    def test_bulma_features_are_used_directly(self):
        pages = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in PAGES)
        self.assertIn("bulma@1.0.4/css/bulma.min.css", pages)
        self.assertIn("navbar", pages)
        self.assertIn("hero", pages)
        self.assertIn("columns", pages)
        self.assertIn("card", pages)
        self.assertIn("notification", pages)
        self.assertIn("progress", pages)
        self.assertIn("is-skeleton", pages)
        self.assertIn("skeleton-lines", pages)

    def test_theme_switcher_uses_bulma_data_theme_contract(self):
        script = (ROOT / "assets/ui.js").read_text(encoding="utf-8")
        self.assertIn("setAttribute('data-theme', value)", script)
        self.assertIn("removeAttribute('data-theme')", script)
        self.assertIn("['system', 'light', 'dark']", script)
        self.assertNotIn("style.", script)

    def test_lucide_is_the_icon_system(self):
        pages = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in PAGES)
        script = (ROOT / "assets/ui.js").read_text(encoding="utf-8")
        self.assertIn("lucide@1.33.0/dist/umd/lucide.js", pages)
        self.assertIn("data-lucide=", pages)
        self.assertIn("lucide.createIcons", script)
        for symbol in ("◐", "Δ", "Σ", "✓"):
            self.assertNotIn(symbol, pages)

    def test_old_generated_homepage_slogans_are_removed(self):
        pages = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in PAGES)
        for phrase in (
            "Improve what can",
            "Not just the jackpot ads",
            "Separate what is",
            "Probability first · evidence labelled",
        ):
            self.assertNotIn(phrase, pages)

    def test_pages_deployment_tracks_all_user_facing_surfaces(self):
        workflow = (ROOT / ".github/workflows/deploy.yml").read_text(encoding="utf-8")
        for path in ("index.html", "benchmark.html", "games.html", "service-worker.js", "assets/**"):
            self.assertIn(path, workflow)
        self.assertIn("Validate static site payload", workflow)
        self.assertIn("test ! -f assets/app.css", workflow)
        self.assertIn("! grep -R -n 'style='", workflow)

    def test_pwa_metadata_matches_neutral_redesign(self):
        manifest = json.loads((ROOT / "assets/site.webmanifest").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "Lottery Lab")
        self.assertEqual(manifest["background_color"], "#f5f6f3")
        self.assertEqual(manifest["theme_color"], "#f5f6f3")

    def test_favicon_is_simple_and_has_no_decorative_effects(self):
        favicon = (ROOT / "assets/favicon.svg").read_text(encoding="utf-8")
        self.assertNotIn("linearGradient", favicon)
        self.assertNotIn("feDropShadow", favicon)
        self.assertNotIn("sparkle", favicon.casefold())


if __name__ == "__main__":
    unittest.main()
