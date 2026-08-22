import unittest
from datetime import UTC, date, datetime

from lotto_lab.analysis import build_statistics
from lotto_lab.domain import Draw


class AnalysisTests(unittest.TestCase):
    def test_stats_schema_and_date_range_are_order_independent(self):
        draws = [
            Draw(date(2026, 1, 10), (1, 2, 3, 4, 5, 6), (7, 8)),
            Draw(date(2026, 1, 3), (7, 8, 9, 10, 11, 12), (1, 2)),
        ]
        stats = build_statistics(draws, generated_at=datetime(2026, 1, 11, tzinfo=UTC))
        self.assertEqual(stats["schemaVersion"], 3)
        self.assertEqual(stats["dataset"]["firstDraw"], "2026-01-03")
        self.assertEqual(stats["dataset"]["lastDraw"], "2026-01-10")
        self.assertEqual(stats["game"]["divisionOneCombinations"], 8_145_060)
        self.assertEqual(len(stats["probabilityModel"]["prizeDivisions"]), 6)
        reference = stats["referenceCoverageSet"]
        certificates = reference["metrics"]["probabilityCertificates"]
        self.assertIn("anyPrize", certificates)
        self.assertIn("division4OrBetter", certificates)
        self.assertGreater(certificates["anyPrize"]["bonferroniLowerBound"], 0)
        exact = reference["exactAnyPrize"]
        self.assertTrue(exact["exact"])
        self.assertGreaterEqual(exact["probability"], certificates["anyPrize"]["bonferroniLowerBound"])
        self.assertLessEqual(exact["probability"], certificates["anyPrize"]["firstOrderUnionBound"])


if __name__ == "__main__":
    unittest.main()
