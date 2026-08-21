from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import comb

BALL_COUNT = 45
MAIN_COUNT = 6
SUPPLEMENTARY_COUNT = 2
DIVISION_ONE_COMBINATIONS = comb(BALL_COUNT, MAIN_COUNT)


@dataclass(frozen=True, slots=True)
class Draw:
    date: date
    main: tuple[int, ...]
    supplementary: tuple[int, ...]

    def __post_init__(self) -> None:
        _validate_numbers(self.main, MAIN_COUNT, "main")
        _validate_numbers(self.supplementary, SUPPLEMENTARY_COUNT, "supplementary")
        if set(self.main) & set(self.supplementary):
            raise ValueError(f"{self.date}: main and supplementary numbers overlap")


def _validate_numbers(numbers: tuple[int, ...], expected: int, label: str) -> None:
    if len(numbers) != expected:
        raise ValueError(f"{label} requires {expected} numbers, got {len(numbers)}")
    if len(set(numbers)) != expected:
        raise ValueError(f"{label} numbers must be unique")
    if any(number < 1 or number > BALL_COUNT for number in numbers):
        raise ValueError(f"{label} numbers must be between 1 and {BALL_COUNT}")
