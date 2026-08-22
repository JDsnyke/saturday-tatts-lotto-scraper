from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from .domain import Draw

PRIMARY_SOURCE = "https://au.lottonumbers.com/saturday-lotto/results"
SECONDARY_SOURCE = "https://gnetwork.com.au/saturday-lotto/results"


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_provenance(
    draws: list[Draw],
    *,
    winning_path: str | Path = "winning_numbers.csv",
    supplementary_path: str | Path = "supplementary_numbers.csv",
    generated_at: datetime | None = None,
    secondary_verification: dict | None = None,
) -> dict:
    if not draws:
        raise ValueError("at least one draw is required")
    ordered = sorted(draws, key=lambda draw: draw.date)
    generated_at = generated_at or datetime.now(UTC)
    return {
        "schemaVersion": 1,
        "generatedAt": generated_at.isoformat().replace("+00:00", "Z"),
        "dataset": {
            "drawCount": len(ordered),
            "firstDraw": ordered[0].date.isoformat(),
            "lastDraw": ordered[-1].date.isoformat(),
        },
        "files": {
            str(winning_path): {"sha256": sha256_file(winning_path)},
            str(supplementary_path): {"sha256": sha256_file(supplementary_path)},
        },
        "sources": {
            "primary": PRIMARY_SOURCE,
            "secondary": SECONDARY_SOURCE,
        },
        "secondaryVerification": secondary_verification,
    }


def write_provenance(payload: dict, path: str | Path = "assets/data_provenance.json") -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
