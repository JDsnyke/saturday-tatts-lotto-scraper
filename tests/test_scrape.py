import unittest

from lotto_lab.scrape import archive_draw_links, parse_draw_page


class ScrapeTests(unittest.TestCase):
    def test_archive_link_discovery_deduplicates(self):
        html = '''<a href="/saturday-lotto/results/4697">A</a>
                  <a href="/saturday-lotto/results/4697">A2</a>
                  <a href="/saturday-lotto/results/2026-archive">archive</a>'''
        links = archive_draw_links(html)
        self.assertEqual(links, ["https://au.lottonumbers.com/saturday-lotto/results/4697"])

    def test_parse_draw_page(self):
        balls = "".join(f'<li class="ball">{n}</li>' for n in [2, 6, 8, 12, 22, 43, 13, 28])
        html = f"<html><head><title>Saturday Lotto Results 25 July 2026</title></head><body>{balls}</body></html>"
        draw = parse_draw_page(html)
        self.assertEqual(draw.date.isoformat(), "2026-07-25")
        self.assertEqual(draw.main, (2, 6, 8, 12, 22, 43))
        self.assertEqual(draw.supplementary, (13, 28))


if __name__ == "__main__":
    unittest.main()
