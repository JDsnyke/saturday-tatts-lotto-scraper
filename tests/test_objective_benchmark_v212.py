import unittest

from lotto_lab.benchmark import benchmark_probability_objectives


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


if __name__ == "__main__":
    unittest.main()
