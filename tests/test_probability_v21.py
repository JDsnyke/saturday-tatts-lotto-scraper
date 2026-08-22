import unittest
from math import ceil, comb

from lotto_lab.probability import (
    any_prize_probability,
    at_least_main_match_probability,
    cumulative_division_one_probability,
    division_one_probability,
    main_match_distribution,
    prize_division_probabilities,
    system_entry_combinations,
)


class ProbabilityV21Tests(unittest.TestCase):
    def test_system_entry_counts(self):
        self.assertEqual(system_entry_combinations(6), 1)
        self.assertEqual(system_entry_combinations(7), 7)
        self.assertEqual(system_entry_combinations(8), 28)
        self.assertEqual(system_entry_combinations(20), comb(20, 6))

    def test_main_match_distribution_sums_to_one(self):
        total = sum(row["probability"] for row in main_match_distribution())
        self.assertAlmostEqual(total, 1.0, places=12)

    def test_six_match_equals_division_one(self):
        six = main_match_distribution()[6]["probability"]
        self.assertAlmostEqual(six, division_one_probability(1), places=15)

    def test_at_least_three_is_valid(self):
        probability = at_least_main_match_probability(3)
        self.assertGreater(probability, 0)
        self.assertLess(probability, 1)

    def test_cumulative_probability(self):
        one = division_one_probability(10)
        cumulative = cumulative_division_one_probability(10, 2)
        self.assertAlmostEqual(cumulative, 1 - (1 - one) ** 2)

    def test_prize_division_odds_match_published_structure(self):
        rows = prize_division_probabilities()
        published_style = [ceil(float(row["odds"])) for row in rows]
        self.assertEqual(published_style, [8_145_060, 678_755, 36_690, 733, 298, 53])
        self.assertAlmostEqual(any_prize_probability(), at_least_main_match_probability(3))
        self.assertAlmostEqual(1 / any_prize_probability(), 41.9567300263, places=8)


if __name__ == "__main__":
    unittest.main()
