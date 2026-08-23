import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index.html", "games.html", "benchmark.html")
BULMA = "https://cdn.jsdelivr.net/npm/bulma@1.0.4/css/bulma.min.css"
LUCIDE = "https://unpkg.com/lucide@1.33.0/dist/umd/lucide.js"


class StaticSiteTests(unittest.TestCase):
    def test_browser_assets_and_pwa_references_exist(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        js = (ROOT / "assets/app.js").read_text(encoding="utf-8")
        for path in (
            "assets/ui.js",
            "assets/app.js",
            "assets/site.webmanifest",
            "assets/data_provenance.json",
            "service-worker.js",
        ):
            self.assertTrue((ROOT / path).exists(), path)
        self.assertIn(BULMA, html)
        self.assertIn(LUCIDE, html)
        self.assertIn("assets/ui.js", html)
        self.assertIn("assets/app.js", html)
        self.assertIn("assets/site.webmanifest", html)
        self.assertIn("service-worker.js", js)

    def test_all_pages_use_pinned_bulma_and_lucide(self):
        for name in PAGES:
            html = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn(BULMA, html, name)
            self.assertIn(LUCIDE, html, name)
            self.assertIn("assets/ui.js", html, name)
            self.assertIn("data-lucide=", html, name)

    def test_custom_stylesheets_are_absent(self):
        for name in ("assets/app.css", "assets/games.css", "assets/benchmark.css"):
            self.assertFalse((ROOT / name).exists(), name)
        for page in PAGES:
            html = (ROOT / page).read_text(encoding="utf-8")
            self.assertNotIn("assets/app.css", html)
            self.assertNotIn("assets/games.css", html)
            self.assertNotIn("assets/benchmark.css", html)

    def test_no_inline_presentation_css_or_legacy_custom_components(self):
        content = "\n".join(
            (ROOT / path).read_text(encoding="utf-8")
            for path in (
                *PAGES,
                "assets/ui.js",
                "assets/app.js",
                "assets/games.js",
                "assets/benchmark.js",
                "assets/certificates.js",
            )
        )
        self.assertNotIn("style=", content)
        for legacy in (
            "glass",
            "ticket-card",
            "game-card",
            "benchmark-row",
            "match-bar",
            "frequency-bar",
            "research-note",
            "metric-card",
        ):
            self.assertNotIn(legacy, content)

    def test_direct_javascript_id_references_exist_in_html(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        js = (ROOT / "assets/app.js").read_text(encoding="utf-8")
        html_ids = set(re.findall(r'id="([^"]+)"', html))
        js_ids = set(re.findall(r"\$\('#([^']+)'\)", js))
        self.assertEqual(js_ids - html_ids, set())

    def test_internal_anchor_targets_exist(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        html_ids = set(re.findall(r'id="([^"]+)"', html))
        anchors = set(re.findall(r'href="#([^"]+)"', html))
        self.assertEqual(anchors - html_ids, set())


if __name__ == "__main__":
    unittest.main()
