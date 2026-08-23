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


if __name__ == "__main__":
    unittest.main()
