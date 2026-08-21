import unittest
from collections import Counter

from lotto_lab.tickets import generate_coverage_tickets, generate_random_tickets, ticket_metrics


class TicketTests(unittest.TestCase):
    def assert_valid(self, tickets, count):
        self.assertEqual(len(tickets), count)
        self.assertEqual(len(set(tickets)), count)
        for ticket in tickets:
            self.assertEqual(len(ticket), 6)
            self.assertEqual(len(set(ticket)), 6)
            self.assertTrue(all(1 <= number <= 45 for number in ticket))

    def test_random_tickets_are_reproducible_with_seed(self):
        a = generate_random_tickets(10, seed="test")
        b = generate_random_tickets(10, seed="test")
        self.assertEqual(a, b)
        self.assert_valid(a, 10)

    def test_coverage_mode_balances_number_usage(self):
        tickets = generate_coverage_tickets(10, seed="test")
        self.assert_valid(tickets, 10)
        usage = Counter(number for ticket in tickets for number in ticket)
        counts = [usage[number] for number in range(1, 46)]
        self.assertLessEqual(max(counts) - min(counts), 1)
        self.assertEqual(ticket_metrics(tickets)["uniqueNumbers"], 45)


if __name__ == "__main__":
    unittest.main()
