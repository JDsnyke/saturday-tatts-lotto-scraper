import tempfile
import unittest
from pathlib import Path

from lotto_lab.data import DataValidationError, load_draws


class DataTests(unittest.TestCase):
    def test_load_draws_sorts_and_merges(self):
        with tempfile.TemporaryDirectory() as tmp:
            main = Path(tmp) / "main.csv"
            supp = Path(tmp) / "supp.csv"
            main.write_text("2026-01-10,1,2,3,4,5,6\n2026-01-03,7,8,9,10,11,12\n", encoding="utf-8")
            supp.write_text("2026-01-03,13,14\n2026-01-10,7,8\n", encoding="utf-8")
            draws = load_draws(main, supp)
            self.assertEqual(draws[0].date.isoformat(), "2026-01-03")
            self.assertEqual(draws[-1].main, (1, 2, 3, 4, 5, 6))

    def test_rejects_duplicate_numbers(self):
        with tempfile.TemporaryDirectory() as tmp:
            main = Path(tmp) / "main.csv"
            supp = Path(tmp) / "supp.csv"
            main.write_text("2026-01-10,1,1,3,4,5,6\n", encoding="utf-8")
            supp.write_text("2026-01-10,7,8\n", encoding="utf-8")
            with self.assertRaises(DataValidationError):
                load_draws(main, supp)


if __name__ == "__main__":
    unittest.main()
