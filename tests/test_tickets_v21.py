import unittest

from lotto_lab.crowding import crowding_penalty, generate_anti_crowding_tickets
from lotto_lab.tickets import (
    generate_coverage_tickets,
    generate_random_tickets,
    subset_coverage,
    ticket_metrics,
)


class TicketsV21Tests(unittest.TestCase):
    def test_subset_coverage_counts(self):
        tickets = [(1, 2, 3, 4, 5, 6), (1, 2, 7, 8, 9, 10)]
        triples = subset_coverage(tickets, 3)
        self.assertEqual(triples["placements"], 40)
        self.assertEqual(triples["repeated"], 0)
        self.assertEqual(triples["efficiency"], 1.0)

    def test_optimizer_has_strong_triple_efficiency(self):
        tickets = generate_coverage_tickets(20, seed="coverage-test", candidates_per_ticket=500)
        metrics = ticket_metrics(tickets)
        self.assertEqual(len(tickets), len(set(tickets)))
        self.assertGreaterEqual(metrics["tripleCoverage"]["efficiency"], 0.98)

    def test_optimizer_beats_seeded_random_triple_coverage(self):
        coverage = generate_coverage_tickets(30, seed="compare", candidates_per_ticket=500)
        random = generate_random_tickets(30, seed="compare")
        self.assertGreaterEqual(
            subset_coverage(coverage, 3)["unique"],
            subset_coverage(random, 3)["unique"],
        )

    def test_anti_crowding_reduces_mean_penalty(self):
        anti = generate_anti_crowding_tickets(20, seed="crowd", candidate_pool=2000)
        random = generate_random_tickets(20, seed="crowd")
        anti_mean = sum(crowding_penalty(ticket) for ticket in anti) / len(anti)
        random_mean = sum(crowding_penalty(ticket) for ticket in random) / len(random)
        self.assertLess(anti_mean, random_mean)


if __name__ == "__main__":
    unittest.main()
