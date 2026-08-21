from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from typing import Iterable

from .domain import Draw, MAIN_COUNT, SUPPLEMENTARY_COUNT


class DataValidationError(ValueError):
    """Raised when a CSV row is malformed or inconsistent."""


def _read_rows(path: str | Path, expected_numbers: int) -> dict[date, tuple[int, ...]]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    rows: dict[date, tuple[int, ...]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        for line_number, row in enumerate(reader, start=1):
            if not row or all(not cell.strip() for cell in row):
                continue
            first = row[0].strip().lower()
            if first in {"date", "draw_date"}:
                continue
            if len(row) != expected_numbers + 1:
                raise DataValidationError(
                    f"{path}:{line_number}: expected {expected_numbers + 1} columns, got {len(row)}"
                )
            try:
                draw_date = date.fromisoformat(row[0].strip())
                numbers = tuple(int(value.strip()) for value in row[1:])
            except ValueError as exc:
                raise DataValidationError(f"{path}:{line_number}: invalid date/number") from exc
            if len(set(numbers)) != expected_numbers:
                raise DataValidationError(f"{path}:{line_number}: duplicate numbers")
            if any(number < 1 or number > 45 for number in numbers):
                raise DataValidationError(f"{path}:{line_number}: number outside 1..45")
            if draw_date in rows:
                raise DataValidationError(f"{path}:{line_number}: duplicate date {draw_date}")
            rows[draw_date] = numbers
    return rows


def load_draws(
    winning_path: str | Path = "winning_numbers.csv",
    supplementary_path: str | Path = "supplementary_numbers.csv",
) -> list[Draw]:
    main_rows = _read_rows(winning_path, MAIN_COUNT)
    supplementary_rows = _read_rows(supplementary_path, SUPPLEMENTARY_COUNT)

    main_dates = set(main_rows)
    supplementary_dates = set(supplementary_rows)
    if main_dates != supplementary_dates:
        missing_supp = sorted(main_dates - supplementary_dates)
        missing_main = sorted(supplementary_dates - main_dates)
        details = []
        if missing_supp:
            details.append(f"missing supplementary rows for {len(missing_supp)} date(s)")
        if missing_main:
            details.append(f"missing winning rows for {len(missing_main)} date(s)")
        raise DataValidationError("; ".join(details))

    draws: list[Draw] = []
    for draw_date in sorted(main_dates):
        draws.append(
            Draw(
                date=draw_date,
                main=tuple(main_rows[draw_date]),
                supplementary=tuple(supplementary_rows[draw_date]),
            )
        )
    return draws


def write_draws(
    draws: Iterable[Draw],
    winning_path: str | Path = "winning_numbers.csv",
    supplementary_path: str | Path = "supplementary_numbers.csv",
) -> None:
    ordered = sorted(draws, key=lambda draw: draw.date, reverse=True)
    with Path(winning_path).open("w", newline="", encoding="utf-8") as main_handle:
        writer = csv.writer(main_handle, lineterminator="\n")
        for draw in ordered:
            writer.writerow([draw.date.isoformat(), *draw.main])
    with Path(supplementary_path).open("w", newline="", encoding="utf-8") as supp_handle:
        writer = csv.writer(supp_handle, lineterminator="\n")
        for draw in ordered:
            writer.writerow([draw.date.isoformat(), *draw.supplementary])
