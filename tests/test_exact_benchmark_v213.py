import unittest

from lotto_lab.exact_benchmark import benchmark_exact_any_prize_objectives


class ExactBenchmarkV213Tests(unittest.TestCase):
    def test_exact_benchmark_reports_exact_strategy_distributions(self):
        result = benchmark_exact_any_prize_objectives(
            5,
            portfolios_per_objective=2,
            random_portfolios=3,
            seed=456,
            candidates_per_ticket=30,
            bootstrap_resamples=100,
        )
        self.assertTrue(result["exact"])
        self.assertTrue(result["divisionOneProbabilityEqual"])
        self.assertTrue(result["portfolioSeedsMatchSimulatedObjectiveBenchmark"])
        for strategy in ("coverage", "anyPrizeBound", "division4Bound", "random"):
            metrics = result["strategies"][strategy]
            self.assertIn("exactAnyPrizeProbability", metrics)
            self.assertIn("anyPrizeBonferroniLowerBound", metrics)
            self.assertIn("bonferroniGap", metrics)
            self.assertGreaterEqual(metrics["bonferroniGap"]["min"], 0)
        self.assertIn("anyPrizeBoundVsCoverage", result["comparisons"])
        self.assertIn("coverageVsRandom", result["comparisons"])

    def test_exact_benchmark_rejects_more_than_twelve_games(self):
        with self.assertRaisesRegex(ValueError, "between 1 and 12"):
            benchmark_exact_any_prize_objectives(
                13,
                portfolios_per_objective=2,
                random_portfolios=2,
                candidates_per_ticket=20,
                bootstrap_resamples=100,
            )


if __name__ == "__main__":
    unittest.main()
