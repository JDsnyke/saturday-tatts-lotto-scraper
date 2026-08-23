from __future__ import annotations

from dataclasses import asdict, dataclass

from .game_catalog import GameDefinition, SourceRef


@dataclass(frozen=True)
class RaffleSnapshot:
    """Current or recent draw metadata that must not be mistaken for fixed game odds."""

    draw_id: str
    status: str
    draw_date: str
    close_date: str | None = None
    ticket_price_from: float | None = None
    maximum_entries: int | None = None
    minimum_possible_entries: int | None = None
    first_prize_value: float | None = None
    first_prize_label: str | None = None
    source: SourceRef | None = None
    probability_note: str = (
        "Entry-capacity metadata is not automatically an exact 1-in-X probability; use the operator's "
        "valid-entry rule for the specific draw."
    )

    def to_dict(self) -> dict:
        return asdict(self)


YOURTOWN_ODDS = SourceRef(
    "yourtown — First Prize odds depend on tickets sold",
    "https://support.yourtown.com.au/hc/en-us/articles/360000830493-What-are-the-odds-of-winning-First-Prize",
)
YOURTOWN_PRICE = SourceRef(
    "yourtown — most Prize Home draws have 500,000 tickets available",
    "https://support.yourtown.com.au/hc/en-us/articles/360002282953-Why-are-yourtown-s-tickets-15-and-other-charities-tickets-cheaper",
)
MATER_HOME_327 = SourceRef(
    "Mater Prize Home 327 terms",
    "https://www.materlotteries.com.au/mater-prize-home/terms-and-conditions/327",
)
MATER_CARS_130 = SourceRef(
    "Mater Cars for Cancer 130 terms",
    "https://www.materlotteries.com.au/mater-cars-for-cancer/terms-and-conditions/130",
)
DREAM_HOME_CURRENT = SourceRef(
    "Dream Home Art Union — current prize-home draws",
    "https://dreamhomeartunion.com.au/",
)
DREAM_HOME_FAQ = SourceRef(
    "Dream Home Art Union — official FAQ",
    "https://dreamhomeartunion.com.au/faq",
)
ENDEAVOUR_HOME_468 = SourceRef(
    "Endeavour Foundation Prize Home 468",
    "https://www.endeavourlotteries.com.au/endeavour-foundation/terms-and-conditions",
)
ENDEAVOUR_PAYDAY_221 = SourceRef(
    "Endeavour Pay Day 221 terms",
    "https://www.endeavourlotteries.com.au/pay-day/terms-and-conditions/221",
)


ALTERNATIVE_GAMES: dict[str, GameDefinition] = {
    "yourtown-prize-home": GameDefinition(
        slug="yourtown-prize-home",
        name="yourtown Prize Home Draws",
        operator="yourtown",
        mechanic="variable-raffle",
        jurisdictions=("Australia — draw terms apply",),
        schedule="Prize Home draws run through the year",
        description=(
            "Charity art-union Prize Home draws supporting services including Kids Helpline. "
            "First-prize odds depend on actual tickets sold."
        ),
        sources=(YOURTOWN_ODDS, YOURTOWN_PRICE),
        notes=(
            "yourtown states that most Prize Home draws have 500,000 tickets available and gives "
            "1 in 500,000 only as the sold-out one-ticket example. Actual First Prize odds are tied "
            "to tickets sold, so the catalog does not hard-code a fixed denominator.",
        ),
    ),
    "mater-prize-home": GameDefinition(
        slug="mater-prize-home",
        name="Mater Prize Home",
        operator="Mater Lotteries",
        mechanic="variable-raffle",
        jurisdictions=("QLD", "NSW", "ACT", "VIC", "NT"),
        schedule="Draw-specific Prize Home art unions",
        description="Mater Foundation Prize Home art union with draw-specific entry capacity and bundles.",
        sources=(MATER_HOME_327,),
        notes=(
            "Prize Home 327 terms show available entries can vary materially with bundle purchases, "
            "so the possible entry count is not represented as a fixed one-ticket odds denominator.",
        ),
    ),
    "mater-cars-for-cancer": GameDefinition(
        slug="mater-cars-for-cancer",
        name="Mater Cars for Cancer",
        operator="Mater Lotteries",
        mechanic="variable-raffle",
        jurisdictions=("QLD", "NSW", "ACT", "VIC", "SA", "NT"),
        schedule="Draw-specific vehicle/prize package lotteries",
        description="Mater Foundation vehicle and lifestyle prize lottery supporting cancer research.",
        sources=(MATER_CARS_130,),
        notes=(
            "Current Lottery 130 permits up to 85,117 tickets at $30 each. The cap is useful scarcity "
            "metadata but is not promoted as exact odds unless the valid-entry mechanics make it exact.",
        ),
    ),
    "dream-home-art-union": GameDefinition(
        slug="dream-home-art-union",
        name="Dream Home Art Union (RSL Queensland)",
        operator="RSL Queensland",
        mechanic="variable-raffle",
        jurisdictions=("Australia — draw terms and permits apply",),
        schedule="Recurring Dream Home art-union draws",
        description=(
            "Formerly RSL Art Union; recurring multi-million-dollar prize-home draws supporting veterans "
            "and their families."
        ),
        sources=(DREAM_HOME_CURRENT, DREAM_HOME_FAQ),
        notes=(
            "Draw 434 is scheduled for 20 October 2026. Entry capacity and bonus-entry structures are "
            "draw-specific and must be sourced from that draw's terms before odds are computed.",
        ),
    ),
    "endeavour-prize-home": GameDefinition(
        slug="endeavour-prize-home",
        name="Endeavour Foundation Prize Home",
        operator="Endeavour Lotteries",
        mechanic="variable-raffle",
        jurisdictions=("Australia — draw terms and permits apply",),
        schedule="Recurring Prize Home art unions",
        description="Prize Home art unions supporting people with intellectual disability.",
        sources=(ENDEAVOUR_HOME_468,),
        notes=(
            "Prize Home 468 was drawn 20 August 2026. Bundle bonus tickets change entries per dollar, "
            "so purchase price alone is not an odds denominator.",
        ),
    ),
    "endeavour-pay-day": GameDefinition(
        slug="endeavour-pay-day",
        name="Endeavour Pay Day",
        operator="Endeavour Lotteries",
        mechanic="variable-raffle",
        jurisdictions=("Australia — eligibility and draw terms apply",),
        schedule="Recurring cash/vehicle prize draws",
        description=(
            "Lower-cost fixed-capacity prize draws supporting Endeavour Foundation charitable causes."
        ),
        sources=(ENDEAVOUR_PAYDAY_221,),
        notes=(
            "Pay Day 221 is limited to 200,000 tickets at $5 each and is drawn 8 October 2026. "
            "The ticket cap is exposed as capacity metadata, not silently converted to exact odds.",
        ),
    ),
}


ALTERNATIVE_SNAPSHOTS: dict[str, RaffleSnapshot] = {
    "yourtown-prize-home": RaffleSnapshot(
        draw_id="typical Prize Home draw",
        status="product-family guidance",
        draw_date="varies",
        ticket_price_from=15.0,
        maximum_entries=500_000,
        first_prize_label="Luxury Prize Home package varies by draw",
        source=YOURTOWN_ODDS,
        probability_note=(
            "yourtown explicitly states First Prize odds depend on tickets sold. If 500,000 of 500,000 "
            "tickets sell, one ticket is 1 in 500,000; if fewer sell, the denominator is lower."
        ),
    ),
    "mater-prize-home": RaffleSnapshot(
        draw_id="327",
        status="open/current on source check",
        close_date="2026-10-20",
        draw_date="2026-10-23",
        ticket_price_from=2.0,
        minimum_possible_entries=13_455_147,
        maximum_entries=22_805_334,
        first_prize_value=5_382_059.0,
        first_prize_label="$5.382M Sunshine Coast Prize Home package",
        source=MATER_HOME_327,
        probability_note=(
            "Mater states available entries can range from 13,455,147 to 22,805,334 depending on "
            "bundle purchases. This range must not be collapsed into one fixed odds figure."
        ),
    ),
    "mater-cars-for-cancer": RaffleSnapshot(
        draw_id="130",
        status="open/current on source check",
        close_date="2026-09-13",
        draw_date="2026-09-16",
        ticket_price_from=30.0,
        maximum_entries=85_117,
        first_prize_value=510_707.0,
        first_prize_label="$510,707 Cars for Cancer prize package",
        source=MATER_CARS_130,
        probability_note=(
            "The terms permit up to 85,117 tickets. The catalog treats this as a maximum ticket supply, "
            "not a guaranteed denominator for the final valid-entry draw."
        ),
    ),
    "dream-home-art-union": RaffleSnapshot(
        draw_id="434",
        status="open/current on source check",
        draw_date="2026-10-20",
        ticket_price_from=5.0,
        first_prize_value=10_200_000.0,
        first_prize_label="$10.2M Currumbin Gold Coast Dream",
        source=DREAM_HOME_CURRENT,
        probability_note=(
            "Current official page verifies the draw/prize/ticket-from price. Exact first-prize odds are "
            "left variable until Draw 434 entry-capacity terms are captured from an authoritative source."
        ),
    ),
    "endeavour-prize-home": RaffleSnapshot(
        draw_id="468",
        status="sold out / drawn",
        draw_date="2026-08-20",
        ticket_price_from=10.0,
        first_prize_value=3_700_000.0,
        first_prize_label="$3.7M Maleny Home of the Year",
        source=ENDEAVOUR_HOME_468,
        probability_note=(
            "Bundle purchases included bonus tickets. This snapshot demonstrates the product family but "
            "does not treat dollars spent as a fixed probability denominator."
        ),
    ),
    "endeavour-pay-day": RaffleSnapshot(
        draw_id="221",
        status="current on source check",
        draw_date="2026-10-08",
        ticket_price_from=5.0,
        maximum_entries=200_000,
        first_prize_value=200_000.0,
        first_prize_label="$200K gold or vehicle/gold package",
        source=ENDEAVOUR_PAYDAY_221,
        probability_note=(
            "The operator advertises a 200,000-ticket limit. The catalog exposes the cap and avoids "
            "assuming all 200,000 entries will be valid/sold unless the specific draw terms require it."
        ),
    ),
}


def list_alternative_games() -> list[GameDefinition]:
    return sorted(ALTERNATIVE_GAMES.values(), key=lambda game: (game.operator, game.name))


def get_alternative_game(slug: str) -> GameDefinition:
    try:
        return ALTERNATIVE_GAMES[slug]
    except KeyError as exc:
        raise KeyError(f"unknown alternative game: {slug}") from exc


def alternative_snapshot(slug: str) -> dict | None:
    snapshot = ALTERNATIVE_SNAPSHOTS.get(slug)
    return None if snapshot is None else snapshot.to_dict()
