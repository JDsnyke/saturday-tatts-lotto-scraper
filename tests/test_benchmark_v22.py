import unittest

from lotto_lab.benchmark import (
    benchmark_portfolio_distributions,
    bootstrap_mean_difference,
    distribution_summary,
    probability_of_superiority,
)


class BenchmarkV22Tests(unittest.TestCase):
    def test_distribution_summary_quantiles_are_ordered(self):
        summary = distribution_summary([5, 1, 4, 2, 3])
        self.assertEqual(summary["count"], 5)
        self.assertLessEqual(summary["p05"], summary["median"])
        self.assertLessEqual(summary["median"], summary["p95"])
        self.assertEqual(summary["mean"], 3)

    def test_probability_of_superiority_respects_direction(self):
        self.assertEqual(probability_of_superiority([3, 4], [1, 2]), 1.0)
        self.assertEqual(
            probability_of_superiority([1, 2], [3, 4], direction="lower"),
            1.0,
        )

    def test_bootstrap_difference_is_reproducible(self):
        first = bootstrap_mean_difference(
            [0.9, 0.91, 0.92], [0.8, 0.81, 0.82], resamples=200, seed=7
        )
        second = bootstrap_mean_difference(
            [0.9, 0.91, 0.92], [0.8, 0.81, 0.82], resamples=200, seed=7
        )
        self.assertEqual(first, second)
        self.assertGreater(first[0], 0)

    def test_multiseed_benchmark_keeps_division_one_equal(self):
        result = benchmark_portfolio_distributions(
            6,
            coverage_portfolios=3,
            random_portfolios=6,
            trials=120,
            seed=123,
            candidates_per_ticket=40,
            bootstrap_resamples=200,
        )
        self.assertTrue(result["divisionOneProbabilityEqual"])
        self.assertEqual(result["coveragePortfolios"], 3)
        self.assertEqual(result["randomPortfolios"], 6)
        self.assertIn("tripleCoverageEfficiency", result["metrics"])
        self.assertIn("anyPrizeRate", result["metrics"])

    def test_coverage_distribution_improves_structural_efficiency(self):
        result = benchmark_portfolio_distributions(
            10,
            coverage_portfolios=4,
            random_portfolios=10,
            trials=100,
            seed=2026,
            candidates_per_ticket=60,
            bootstrap_resamples=200,
        )
        triple = result["metrics"]["tripleCoverageEfficiency"]
        quad = result["metrics"]["quadCoverageEfficiency"]
        self.assertGreaterEqual(triple["coverage"]["mean"], triple["random"]["mean"])
        self.assertGreaterEqual(quad["coverage"]["mean"], quad["random"]["mean"])


if __name__ == "__main__":
    unittest.main()
