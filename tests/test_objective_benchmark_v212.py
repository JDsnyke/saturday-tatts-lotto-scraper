import unittest

from lotto_lab.benchmark import _exact_equality_override, benchmark_probability_objectives


class ObjectiveBenchmarkV212Tests(unittest.TestCase):
    def test_objective_benchmark_keeps_division_one_equal_and_reports_certificates(self):
        result = benchmark_probability_objectives(
            6,
            portfolios_per_objective=3,
            random_portfolios=4,
            trials=400,
            seed=321,
            candidates_per_ticket=40,
            bootstrap_resamples=100,
        )
        self.assertTrue(result["divisionOneProbabilityEqual"])
        self.assertIn("coverage", result["strategies"])
        self.assertIn("anyPrizeBound", result["strategies"])
        self.assertIn("division4Bound", result["strategies"])
        self.assertIn("random", result["strategies"])
        self.assertIn(
            "anyPrizeBonferroniLowerBound",
            result["strategies"]["anyPrizeBound"],
        )
        self.assertIn(
            "division4GloballyOptimal",
            result["strategies"]["division4Bound"],
        )
        self.assertIn("anyPrizeBoundVsCoverage", result["comparisons"])
        self.assertIn("division4BoundVsCoverage", result["comparisons"])

    def test_exact_equality_suppresses_monte_carlo_inference(self):
        left = [
            {
                "division4GloballyOptimal": 1.0,
                "division4CertifiedProbability": 0.0139,
                "division4OrBetterRate": 0.016,
            },
            {
                "division4GloballyOptimal": 1.0,
                "division4CertifiedProbability": 0.0139,
                "division4OrBetterRate": 0.015,
            },
        ]
        right = [
            {
                "division4GloballyOptimal": 1.0,
                "division4CertifiedProbability": 0.0139,
                "division4OrBetterRate": 0.012,
            },
            {
                "division4GloballyOptimal": 1.0,
                "division4CertifiedProbability": 0.0139,
                "division4OrBetterRate": 0.013,
            },
        ]
        comparison = _exact_equality_override(
            left,
            right,
            simulated_metric="division4OrBetterRate",
            exact_metric="division4CertifiedProbability",
            certificate_metric="division4GloballyOptimal",
        )
        self.assertIsNotNone(comparison)
        self.assertTrue(comparison["inferenceSuppressed"])
        self.assertEqual(comparison["exactProbabilityDifference"], 0.0)
        self.assertIsNone(comparison["bootstrapMeanDifferenceCi95"])
        self.assertIsNone(comparison["probabilityOfSuperiority"])
        self.assertNotEqual(comparison["descriptiveSimulatedMeanDifference"], 0.0)


if __name__ == "__main__":
    unittest.main()
