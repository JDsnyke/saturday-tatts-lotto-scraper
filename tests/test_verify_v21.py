import unittest
from datetime import date
from pathlib import Path

from lotto_lab.domain import Draw
from lotto_lab.verify import parse_secondary_results, verify_latest_draws

FIXTURES = Path(__file__).parent / "fixtures"


class VerifyV21Tests(unittest.TestCase):
    def test_parse_secondary_fixture(self):
        html = (FIXTURES / "gnetwork_results_4697.html").read_text(encoding="utf-8")
        rows = parse_secondary_results(html)
        self.assertEqual(rows[0].draw_number, 4697)
        self.assertEqual(rows[0].main, (12, 43, 2, 22, 8, 6))
        self.assertEqual(rows[0].supplementary, (28, 13))

    def test_verify_by_main_and_supp_sets(self):
        html = (FIXTURES / "gnetwork_results_4697.html").read_text(encoding="utf-8")
        draws = [Draw(date(2026, 7, 25), (2, 6, 8, 12, 22, 43), (13, 28))]
        report = verify_latest_draws(draws, parse_secondary_results(html), limit=1)
        self.assertTrue(report["ok"])
        self.assertEqual(report["matches"][0]["drawNumber"], 4697)
        self.assertEqual(
            report["matches"][0]["sourceUrl"],
            "https://gnetwork.com.au/saturday-lotto/draw_4697",
        )


if __name__ == "__main__":
    unittest.main()
