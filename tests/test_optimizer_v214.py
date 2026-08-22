import unittest

from lotto_lab.optimizer import generate_exact_local_tickets, optimise_any_prize_exact
from lotto_lab.portfolio import exact_any_prize_probability, portfolio_probability_certificate
from lotto_lab.tickets import generate_coverage_tickets


class ExactLocalSearchV214Tests(unittest.TestCase):
    def test_local_search_never_worsens_exact_any_prize_probability(self):
        baseline = generate_coverage_tickets(6, seed="local-monotonic", candidates_per_ticket=40)
        result = optimise_any_prize_exact(
            baseline,
            seed="local-monotonic-search",
            iterations=1,
            exact_shortlist=2,
            exploration_candidates=0,
        )
        self.assertGreaterEqual(
            result["finalExactAnyPrize"]["anyPrizeWinningMainSets"],
            result["baselineExactAnyPrize"]["anyPrizeWinningMainSets"],
        )
        for step in result["history"]:
            self.assertGreater(
                step["afterAnyPrizeWinningMainSets"],
                step["beforeAnyPrizeWinningMainSets"],
            )

    def test_local_search_preserves_existing_division4_global_certificate(self):
        baseline = [
            (1, 2, 3, 4, 5, 6),
            (7, 8, 9, 10, 11, 12),
            (13, 14, 15, 16, 17, 18),
            (19, 20, 21, 22, 23, 24),
        ]
        self.assertTrue(
            portfolio_probability_certificate(baseline, threshold=4)["globallyOptimalForTicketCount"]
        )
        result = optimise_any_prize_exact(
            baseline,
            seed="preserve-d4",
            iterations=1,
            exact_shortlist=2,
            exploration_candidates=0,
        )
        final = [tuple(ticket) for ticket in result["tickets"]]
        self.assertTrue(result["preservedDivision4Optimality"])
        self.assertTrue(
            portfolio_probability_certificate(final, threshold=4)["globallyOptimalForTicketCount"]
        )

    def test_generator_is_deterministic_and_returns_distinct_tickets(self):
        kwargs = {
            "candidates_per_ticket": 40,
            "iterations": 1,
            "exact_shortlist": 2,
            "exploration_candidates": 0,
        }
        left = generate_exact_local_tickets(5, seed="deterministic-local", **kwargs)
        right = generate_exact_local_tickets(5, seed="deterministic-local", **kwargs)
        self.assertEqual(left, right)
        self.assertEqual(len(left), len(set(left)))
        self.assertEqual(len(left), 5)

    def test_zero_iterations_returns_same_exact_probability(self):
        baseline = generate_coverage_tickets(5, seed="zero-local", candidates_per_ticket=40)
        result = optimise_any_prize_exact(baseline, iterations=0)
        exact = exact_any_prize_probability(baseline)
        self.assertEqual(result["finalExactAnyPrize"], exact)
        self.assertEqual(result["improvementWinningMainSets"], 0)
        self.assertEqual(result["acceptedMoves"], 0)

    def test_duplicate_portfolio_is_rejected(self):
        ticket = (1, 2, 3, 4, 5, 6)
        with self.assertRaises(ValueError):
            optimise_any_prize_exact([ticket, ticket], iterations=0)


if __name__ == "__main__":
    unittest.main()
