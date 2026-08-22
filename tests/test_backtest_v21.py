import random
import unittest
from datetime import date, timedelta

from lotto_lab.domain import Draw
from lotto_lab.simulation import walk_forward_backtest


class BacktestV21Tests(unittest.TestCase):
    def test_walk_forward_has_equal_steps_and_metrics(self):
        rng = random.Random(7)
        draws = []
        start = date(2025, 1, 4)
        for i in range(18):
            balls = rng.sample(range(1, 46), 8)
            draws.append(Draw(start + timedelta(days=7 * i), tuple(balls[:6]), tuple(balls[6:])))
        result = walk_forward_backtest(draws, ticket_count=5, max_steps=8, seed=99)
        self.assertEqual(result["steps"], 8)
        self.assertIn("atLeast3Rate", result["coverage"])
        self.assertIn("meanTripleCoverageEfficiency", result["random"])


if __name__ == "__main__":
    unittest.main()
