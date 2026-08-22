import unittest

from lotto_lab.search_benchmark import benchmark_exact_local_search


class SearchBenchmarkV214Tests(unittest.TestCase):
    def test_paired_benchmark_never_reports_negative_exact_improvement(self):
        result = benchmark_exact_local_search(
            5,
            portfolios=2,
            seed=214,
            candidates_per_ticket=40,
            iterations=1,
            exact_shortlist=1,
            exploration_candidates=0,
            bootstrap_resamples=100,
        )
        self.assertTrue(result["exact"])
        self.assertTrue(result["pairedDesign"])
        self.assertTrue(result["divisionOneProbabilityEqual"])
        self.assertTrue(result["allExactImprovementsNonNegative"])
        self.assertTrue(result["allExistingDivision4OptimaPreserved"])
        self.assertGreaterEqual(result["improvementProbability"]["min"], 0)
        self.assertEqual(result["portfolioPairs"], 2)


if __name__ == "__main__":
    unittest.main()
