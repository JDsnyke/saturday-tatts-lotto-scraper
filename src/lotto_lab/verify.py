from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

from .domain import Draw

SECONDARY_URL = "https://gnetwork.com.au/saturday-lotto/results"
USER_AGENT = "SaturdayLottoResearchBot/2.1 (+https://github.com/JDsnyke/saturday-tatts-lotto-scraper)"
DRAW_NUMBER = re.compile(r"#?(\d{4,})")
NUMBER = re.compile(r"\b([1-9]|[1-3]\d|4[0-5])\b")


@dataclass(frozen=True, slots=True)
class SecondaryDraw:
    draw_number: int
    main: tuple[int, ...]
    supplementary: tuple[int, ...]

    @property
    def signature(self) -> tuple[frozenset[int], frozenset[int]]:
        return frozenset(self.main), frozenset(self.supplementary)


def fetch_secondary_html(timeout: int = 20) -> str:
    request = Request(SECONDARY_URL, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    with urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed https source
        return response.read().decode("utf-8", errors="replace")


def parse_secondary_results(html: str) -> list[SecondaryDraw]:
    soup = BeautifulSoup(html, "html.parser")
    results: list[SecondaryDraw] = []
    seen: set[int] = set()
    for row in soup.select("tr"):
        cells = [" ".join(cell.stripped_strings) for cell in row.find_all(["th", "td"])]
        if len(cells) < 2:
            continue
        draw_match = DRAW_NUMBER.search(cells[0])
        numbers = [int(value) for value in NUMBER.findall(cells[1])]
        if not draw_match or len(numbers) < 8:
            continue
        draw_number = int(draw_match.group(1))
        if draw_number in seen:
            continue
        seen.add(draw_number)
        results.append(SecondaryDraw(draw_number, tuple(numbers[:6]), tuple(numbers[6:8])))
    return results


def verify_latest_draws(draws: list[Draw], secondary: list[SecondaryDraw], limit: int = 10) -> dict:
    if limit < 1:
        raise ValueError("limit must be positive")
    latest = sorted(draws, key=lambda draw: draw.date, reverse=True)[:limit]
    by_signature = {result.signature: result for result in secondary}
    verified = []
    missing = []
    for draw in latest:
        signature = frozenset(draw.main), frozenset(draw.supplementary)
        match = by_signature.get(signature)
        if match:
            verified.append(
                {
                    "date": draw.date.isoformat(),
                    "drawNumber": match.draw_number,
                    "sourceUrl": f"https://gnetwork.com.au/saturday-lotto/draw_{match.draw_number}",
                }
            )
        else:
            missing.append(draw.date.isoformat())
    return {
        "requested": len(latest),
        "verified": len(verified),
        "ok": not missing,
        "matches": verified,
        "missingDates": missing,
        "secondarySource": SECONDARY_URL,
    }
