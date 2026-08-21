from __future__ import annotations

import re
import time
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

from .data import DataValidationError, load_draws, write_draws
from .domain import Draw

BASE_URL = "https://au.lottonumbers.com"
ARCHIVE_TEMPLATE = BASE_URL + "/saturday-lotto/results/{year}-archive"
DATE_PATTERN = re.compile(r"(\d{1,2}\s+[A-Za-z]+\s+\d{4})")
DRAW_LINK_PATTERN = re.compile(r"^/saturday-lotto/results/\d")
USER_AGENT = "SaturdayLottoResearchBot/2.0 (+https://github.com/JDsnyke/saturday-tatts-lotto-scraper)"


def _fetch(url: str, timeout: int = 20) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    with urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed https source
        return response.read().decode("utf-8", errors="replace")


def parse_draw_page(html: str) -> Draw:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    match = DATE_PATTERN.search(title)
    if not match:
        match = DATE_PATTERN.search(soup.get_text(" ", strip=True))
    if not match:
        raise ValueError("draw date not found")
    draw_date = datetime.strptime(match.group(1), "%d %B %Y").date()

    values = []
    for node in soup.select("li.ball"):
        text = node.get_text(" ", strip=True)
        number_match = re.search(r"\b([1-9]|[1-3]\d|4[0-5])\b", text)
        if number_match:
            values.append(int(number_match.group(1)))
    if len(values) < 8:
        raise ValueError(f"expected at least 8 drawn balls, found {len(values)}")
    return Draw(draw_date, tuple(values[:6]), tuple(values[6:8]))


def archive_draw_links(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links: list[str] = []
    seen: set[str] = set()
    for anchor in soup.find_all("a", href=True):
        href = str(anchor["href"])
        if not DRAW_LINK_PATTERN.match(href) or "archive" in href:
            continue
        url = urljoin(BASE_URL, href)
        if url not in seen:
            seen.add(url)
            links.append(url)
    return links


def scrape_year(year: int, *, pause_seconds: float = 0.15) -> list[Draw]:
    archive_html = _fetch(ARCHIVE_TEMPLATE.format(year=year))
    draws: list[Draw] = []
    for url in archive_draw_links(archive_html):
        try:
            draws.append(parse_draw_page(_fetch(url)))
        except (OSError, ValueError) as exc:
            print(f"warning: {url}: {exc}")
        if pause_seconds:
            time.sleep(pause_seconds)
    unique = {draw.date: draw for draw in draws}
    return sorted(unique.values(), key=lambda draw: draw.date)


def refresh_dataset(
    winning_path: str | Path = "winning_numbers.csv",
    supplementary_path: str | Path = "supplementary_numbers.csv",
    *,
    from_year: int | None = None,
    to_year: int | None = None,
) -> tuple[int, int]:
    today = date.today()
    to_year = to_year or today.year
    from_year = from_year or to_year
    if from_year > to_year:
        raise ValueError("from_year cannot be greater than to_year")

    existing: dict[date, Draw] = {}
    try:
        existing = {draw.date: draw for draw in load_draws(winning_path, supplementary_path)}
    except FileNotFoundError:
        existing = {}
    except DataValidationError as exc:
        message = (
            "Existing dataset is invalid; refusing to overwrite it. "
            "Run `lotto-lab validate` and repair the data first."
        )
        raise DataValidationError(message) from exc

    before = len(existing)
    for year in range(to_year, from_year - 1, -1):
        for draw in scrape_year(year):
            existing[draw.date] = draw
    write_draws(existing.values(), winning_path, supplementary_path)
    return before, len(existing)
