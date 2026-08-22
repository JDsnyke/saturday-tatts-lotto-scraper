import unittest

from lotto_lab.simulation import (
    best_main_match,
    compare_strategies,
    ticket_prize_division,
    wilson_interval,
)


class SimulationV21Tests(unittest.TestCase):
    def test_best_main_match(self):
        tickets = [(1, 2, 3, 4, 5, 6), (7, 8, 9, 10, 11, 12)]
        self.assertEqual(best_main_match(tickets, (1, 2, 3, 20, 21, 22)), 3)

    def test_wilson_interval_contains_rate(self):
        low, high = wilson_interval(50, 100)
        self.assertLess(low, 0.5)
        self.assertGreater(high, 0.5)

    def test_comparison_same_division_one_probability(self):
        result = compare_strategies(10, trials=1000, seed=123)
        a = result["coverage"]["metrics"]["divisionOneProbability"]
        b = result["random"]["metrics"]["divisionOneProbability"]
        self.assertEqual(a, b)
        self.assertIn("anyPrize", result["coverage"]["simulation"])

    def test_prize_division_classification(self):
        main = (1, 2, 3, 4, 5, 6)
        supp = (7, 8)
        self.assertEqual(ticket_prize_division((1, 2, 3, 4, 5, 6), main, supp), 1)
        self.assertEqual(ticket_prize_division((1, 2, 3, 4, 5, 7), main, supp), 2)
        self.assertEqual(ticket_prize_division((1, 2, 3, 4, 5, 9), main, supp), 3)
        self.assertEqual(ticket_prize_division((1, 2, 3, 4, 7, 8), main, supp), 4)
        self.assertEqual(ticket_prize_division((1, 2, 3, 7, 9, 10), main, supp), 5)
        self.assertEqual(ticket_prize_division((1, 2, 3, 9, 10, 11), main, supp), 6)


if __name__ == "__main__":
    unittest.main()
