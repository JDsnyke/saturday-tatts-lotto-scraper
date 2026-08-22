import unittest
from math import comb

from lotto_lab.portfolio import (
    exact_any_prize_probability,
    pair_event_intersection_count,
    portfolio_probability_certificate,
)
from lotto_lab.probability import combination_count


class ExactAnyPrizeV213Tests(unittest.TestCase):
    def test_one_ticket_matches_direct_combinatorics(self):
        ticket = (1, 2, 3, 4, 5, 6)
        result = exact_any_prize_probability([ticket])
        expected_count = sum(comb(6, matches) * comb(39, 6 - matches) for matches in range(3, 7))
        self.assertEqual(result["anyPrizeWinningMainSets"], expected_count)
        self.assertAlmostEqual(result["probability"], expected_count / combination_count())
        self.assertTrue(result["exact"])

    def test_two_disjoint_tickets_match_exact_inclusion_exclusion(self):
        tickets = [
            (1, 2, 3, 4, 5, 6),
            (7, 8, 9, 10, 11, 12),
        ]
        result = exact_any_prize_probability(tickets)
        single_count = sum(comb(6, matches) * comb(39, 6 - matches) for matches in range(3, 7))
        expected_count = 2 * single_count - pair_event_intersection_count(0, 3)
        self.assertEqual(result["anyPrizeWinningMainSets"], expected_count)

    def test_two_overlap_one_tickets_match_exact_inclusion_exclusion(self):
        tickets = [
            (1, 2, 3, 4, 5, 6),
            (1, 7, 8, 9, 10, 11),
        ]
        result = exact_any_prize_probability(tickets)
        single_count = sum(comb(6, matches) * comb(39, 6 - matches) for matches in range(3, 7))
        expected_count = 2 * single_count - pair_event_intersection_count(1, 3)
        self.assertEqual(result["anyPrizeWinningMainSets"], expected_count)

    def test_exact_probability_sits_inside_certified_bounds(self):
        tickets = [
            (1, 2, 3, 4, 5, 6),
            (1, 7, 8, 9, 10, 11),
            (2, 12, 13, 14, 15, 16),
        ]
        exact = exact_any_prize_probability(tickets)["probability"]
        certificate = portfolio_probability_certificate(tickets, threshold=3)
        self.assertGreaterEqual(exact, certificate["bonferroniLowerBound"])
        self.assertLessEqual(exact, certificate["firstOrderUnionBound"])

    def test_runtime_guard_rejects_large_portfolio_by_default(self):
        tickets = [
            tuple(range(start, start + 6))
            for start in range(1, 14)
        ]
        with self.assertRaisesRegex(ValueError, "capped at 12 tickets"):
            exact_any_prize_probability(tickets)


if __name__ == "__main__":
    unittest.main()
