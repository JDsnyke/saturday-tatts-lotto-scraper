import unittest

from lotto_lab.probability import (
    chi_square_uniform,
    combination_count,
    division_one_probability,
    normalized_entropy,
    number_z_score,
)


class ProbabilityTests(unittest.TestCase):
    def test_exact_division_one_combinations(self):
        self.assertEqual(combination_count(), 8_145_060)

    def test_multiple_distinct_ticket_probability_is_linear(self):
        self.assertAlmostEqual(division_one_probability(10), 10 / 8_145_060)

    def test_uniform_entropy_is_one(self):
        self.assertAlmostEqual(normalized_entropy([10] * 45), 1.0)

    def test_uniform_chi_square_is_zero(self):
        self.assertEqual(chi_square_uniform([10] * 45), 0.0)

    def test_expected_frequency_has_zero_z_score(self):
        self.assertAlmostEqual(number_z_score(2, 15), 0.0)


if __name__ == "__main__":
    unittest.main()
