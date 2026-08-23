import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class UiRedesignTests(unittest.TestCase):
    def test_shared_ui_drops_decorative_gradient_layer(self):
        css = (ROOT / "assets/app.css").read_text(encoding="utf-8")
        self.assertNotIn("radial-gradient", css)
        self.assertNotIn("linear-gradient", css)
        self.assertIn(".noise, .aurora { display: none", css)
        self.assertIn("--border:", css)
        self.assertIn("--panel:", css)
        self.assertIn("--panel-soft:", css)

    def test_old_generated_homepage_slogans_are_removed(self):
        pages = "\n".join(
            (ROOT / name).read_text(encoding="utf-8")
            for name in ("index.html", "games.html", "benchmark.html")
        )
        for phrase in (
            "Improve what can",
            "Not just the jackpot ads",
            "Separate what is",
            "Probability first · evidence labelled",
        ):
            self.assertNotIn(phrase, pages)

    def test_pages_deployment_tracks_all_user_facing_surfaces(self):
        workflow = (ROOT / ".github/workflows/deploy.yml").read_text(encoding="utf-8")
        for path in (
            "index.html",
            "benchmark.html",
            "games.html",
            "service-worker.js",
            "assets/**",
        ):
            self.assertIn(path, workflow)
        self.assertIn("Validate static site payload", workflow)

    def test_page_specific_css_no_longer_duplicates_design_system(self):
        for name in ("assets/games.css", "assets/benchmark.css"):
            css = (ROOT / name).read_text(encoding="utf-8")
            self.assertLess(len(css), 500, name)

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
        self.assertIn('fill="#0b6b4f"', favicon)


if __name__ == "__main__":
    unittest.main()
