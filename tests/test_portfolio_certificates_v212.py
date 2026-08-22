import unittest

from lotto_lab.portfolio import (
    pair_event_intersection_count,
    portfolio_probability_certificate,
)
from lotto_lab.probability import at_least_main_match_probability
from lotto_lab.tickets import (
    generate_any_prize_bound_tickets,
    generate_division4_bound_tickets,
    ticket_metrics,
)


class PortfolioCertificateV212Tests(unittest.TestCase):
    def test_pair_intersection_counts_match_exact_combinatorics(self):
        self.assertEqual(pair_event_intersection_count(0, 3), 400)
        self.assertEqual(pair_event_intersection_count(1, 3), 3700)
        self.assertEqual(pair_event_intersection_count(0, 4), 0)
        self.assertEqual(pair_event_intersection_count(1, 4), 0)
        self.assertEqual(pair_event_intersection_count(2, 4), 36)

    def test_overlap_one_makes_division4_events_pairwise_disjoint(self):
        tickets = [
            (1, 2, 3, 4, 5, 6),
            (1, 7, 8, 9, 10, 11),
        ]
        certificate = portfolio_probability_certificate(tickets, threshold=4)
        expected = 2 * at_least_main_match_probability(4)
        self.assertTrue(certificate["pairwiseDisjointEvents"])
        self.assertTrue(certificate["globallyOptimalForTicketCount"])
        self.assertAlmostEqual(certificate["exactProbability"], expected)
        self.assertAlmostEqual(certificate["bonferroniLowerBound"], expected)
        self.assertAlmostEqual(certificate["firstOrderUnionBound"], expected)

    def test_any_prize_certificate_is_a_bound_not_false_exactness(self):
        tickets = [
            (1, 2, 3, 4, 5, 6),
            (7, 8, 9, 10, 11, 12),
        ]
        certificate = portfolio_probability_certificate(tickets, threshold=3)
        self.assertFalse(certificate["pairwiseDisjointEvents"])
        self.assertIsNone(certificate["exactProbability"])
        self.assertLess(
            certificate["bonferroniLowerBound"],
            certificate["firstOrderUnionBound"],
        )

    def test_ticket_metrics_include_both_probability_certificates(self):
        tickets = generate_any_prize_bound_tickets(5, seed="certificate-test")
        certificates = ticket_metrics(tickets)["probabilityCertificates"]
        self.assertIn("anyPrize", certificates)
        self.assertIn("division4OrBetter", certificates)
        self.assertGreater(certificates["anyPrize"]["bonferroniLowerBound"], 0)

    def test_division4_bound_generator_can_produce_global_optimum_for_ten_games(self):
        tickets = generate_division4_bound_tickets(
            10,
            seed="division4-certificate",
            candidates_per_ticket=600,
        )
        certificate = ticket_metrics(tickets)["probabilityCertificates"]["division4OrBetter"]
        self.assertLessEqual(ticket_metrics(tickets)["maxPairwiseOverlap"], 1)
        self.assertTrue(certificate["globallyOptimalForTicketCount"])
        self.assertIsNotNone(certificate["exactProbability"])


if __name__ == "__main__":
    unittest.main()
