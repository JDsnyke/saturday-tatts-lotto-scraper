import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BenchmarkSiteTests(unittest.TestCase):
    def test_benchmark_page_assets_exist(self):
        html = (ROOT / "benchmark.html").read_text(encoding="utf-8")
        js = (ROOT / "assets/benchmark.js").read_text(encoding="utf-8")
        service_worker = (ROOT / "service-worker.js").read_text(encoding="utf-8")
        for path in ("assets/benchmark.css", "assets/benchmark.js", "benchmark.html"):
            self.assertTrue((ROOT / path).exists(), path)
        self.assertIn("assets/benchmark.css", html)
        self.assertIn("assets/benchmark.js", html)
        self.assertIn("referenceBenchmark", js)
        self.assertIn("./benchmark.html", service_worker)
        self.assertIn("./assets/benchmark.js", service_worker)

    def test_benchmark_page_has_evidence_mount_point(self):
        html = (ROOT / "benchmark.html").read_text(encoding="utf-8")
        self.assertIn('id="evidence"', html)
        self.assertIn("Multi-seed", html)


if __name__ == "__main__":
    unittest.main()
