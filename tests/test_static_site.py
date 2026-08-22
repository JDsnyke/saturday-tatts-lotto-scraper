import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class StaticSiteTests(unittest.TestCase):
    def test_browser_assets_and_pwa_references_exist(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        js = (ROOT / "assets/app.js").read_text(encoding="utf-8")
        for path in (
            "assets/app.css",
            "assets/app.js",
            "assets/site.webmanifest",
            "assets/data_provenance.json",
            "service-worker.js",
        ):
            self.assertTrue((ROOT / path).exists(), path)
        self.assertIn("assets/app.css", html)
        self.assertIn("assets/app.js", html)
        self.assertIn("assets/site.webmanifest", html)
        self.assertIn("service-worker.js", js)

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
