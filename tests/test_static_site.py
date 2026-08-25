import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index.html", "games.html", "benchmark.html")
BULMA = "assets/vendor/bulma.min.css"
LUCIDE = "assets/vendor/lucide.js"


class StaticSiteTests(unittest.TestCase):
    def test_browser_assets_and_pwa_references_exist(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        for path in (
            "assets/ui.js",
            "assets/app.js",
            "assets/site.webmanifest",
            "assets/data_provenance.json",
            "service-worker.js",
            "package.json",
            ".github/scripts/prepare_site.sh",
        ):
            self.assertTrue((ROOT / path).exists(), path)
        self.assertIn(BULMA, html)
        self.assertIn(LUCIDE, html)
        self.assertIn("assets/ui.js", html)
        self.assertIn("assets/app.js", html)
        self.assertIn("assets/site.webmanifest", html)

    def test_all_pages_use_local_pinned_bulma_and_lucide(self):
        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(package["dependencies"]["bulma"], "1.0.4")
        self.assertEqual(package["dependencies"]["lucide"], "1.33.0")
        for name in PAGES:
            html = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn(BULMA, html, name)
            self.assertIn(LUCIDE, html, name)
            self.assertNotIn("cdn.jsdelivr.net", html, name)
            self.assertNotIn("unpkg.com", html, name)
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
        for legacy_class in (
            "glass",
            "ticket-card",
            "game-card",
            "benchmark-row",
            "match-bar",
            "frequency-bar",
            "research-note",
            "metric-card",
        ):
            pattern = rf'class=["\'][^"\']*\b{re.escape(legacy_class)}\b'
            self.assertIsNone(re.search(pattern, content), legacy_class)

    def test_publication_build_vendors_dependencies(self):
        script = (ROOT / ".github/scripts/prepare_site.sh").read_text(encoding="utf-8")
        self.assertIn("node_modules/bulma/css/bulma.min.css", script)
        self.assertIn("node_modules/lucide/dist/umd/lucide.js", script)
        self.assertIn("_site/assets/vendor/bulma.min.css", script)
        self.assertIn("_site/assets/vendor/lucide.js", script)

    def test_pages_deploy_regenerates_canonical_stats_before_upload(self):
        workflow = (ROOT / ".github/workflows/deploy.yml").read_text(encoding="utf-8")
        self.assertIn("python -m lotto_lab stats", workflow)
        self.assertIn("bash .github/scripts/prepare_site.sh", workflow)
        self.assertIn("path: '_site'", workflow)
        self.assertIn("stats.get('schemaVersion') == 3", workflow)
        self.assertIn("stats.get('draws')", workflow)

    def test_service_worker_has_no_cross_origin_install_dependency(self):
        worker = (ROOT / "service-worker.js").read_text(encoding="utf-8")
        self.assertIn("australian-lottery-lab-bulma-v3", worker)
        self.assertIn("./assets/vendor/bulma.min.css", worker)
        self.assertIn("./assets/vendor/lucide.js", worker)
        self.assertNotIn("cdn.jsdelivr.net", worker)
        self.assertNotIn("unpkg.com", worker)

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
