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
        self.assertIn("assets/vendor/bulma.min.css", pages)
        self.assertIn("navbar", pages)
        self.assertIn("hero", pages)
        self.assertIn("columns", pages)
        self.assertIn("card", pages)
        self.assertIn("notification", pages)
        self.assertIn("progress", pages)
        self.assertIn("is-skeleton", pages)
        self.assertIn("skeleton-lines", pages)

    def test_theme_switcher_resolves_system_to_explicit_bulma_theme(self):
        script = (ROOT / "assets/ui.js").read_text(encoding="utf-8")
        self.assertIn("setAttribute('data-theme', resolvedTheme)", script)
        self.assertIn("data-theme-preference", script)
        self.assertIn("['system', 'light', 'dark']", script)
        self.assertIn("prefers-color-scheme: dark", script)
        self.assertIn("MutationObserver", script)
        self.assertIn("is-shadowless", script)
        self.assertNotIn("style.", script)

    def test_lucide_is_local_and_the_icon_system(self):
        pages = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in PAGES)
        script = (ROOT / "assets/ui.js").read_text(encoding="utf-8")
        self.assertIn("assets/vendor/lucide.js", pages)
        self.assertNotIn("unpkg.com", pages)
        self.assertIn("data-lucide=", pages)
        self.assertIn("lucide.createIcons", script)
        for symbol in ("◐", "Δ", "Σ", "✓"):
            self.assertNotIn(symbol, pages)

    def test_static_pages_do_not_force_light_variants_or_shadows(self):
        pages = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in PAGES)
        self.assertNotIn(" is-light", pages)
        self.assertNotIn("has-shadow", pages)
        self.assertIn("is-shadowless", pages)

    def test_old_generated_homepage_slogans_are_removed(self):
        pages = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in PAGES)
        for phrase in (
            "Improve what can",
            "Not just the jackpot ads",
            "Separate what is",
            "Probability first · evidence labelled",
        ):
            self.assertNotIn(phrase, pages)

    def test_pages_deployment_builds_and_validates_publication_payload(self):
        workflow = (ROOT / ".github/workflows/deploy.yml").read_text(encoding="utf-8")
        for path in ("index.html", "benchmark.html", "games.html", "service-worker.js", "assets/**"):
            self.assertIn(path, workflow)
        self.assertIn("Build self-contained site payload", workflow)
        self.assertIn("Validate publication payload", workflow)
        self.assertIn("test ! -f _site/assets/app.css", workflow)
        self.assertIn("! grep -R -n 'style='", workflow)
        self.assertIn("schemaVersion", workflow)
        self.assertIn("path: '_site'", workflow)

    def test_browser_gate_checks_contrast_loading_and_mobile_menu(self):
        script = (ROOT / ".github/scripts/browser_audit.mjs").read_text(encoding="utf-8")
        self.assertIn("lowContrast", script)
        self.assertIn("menuOverlap", script)
        self.assertIn("visibleLegacyText", script)
        self.assertIn("page-specific content did not finish loading", script)
        self.assertIn("local Bulma stylesheet did not load", script)

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
