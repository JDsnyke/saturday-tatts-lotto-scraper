from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

Mechanic = Literal[
    "one-pool",
    "two-pool",
    "ordered-digits",
    "ordered-without-replacement",
    "raffle",
    "keno",
    "variable-instant",
    "variable-raffle",
]


@dataclass(frozen=True)
class SourceRef:
    label: str
    url: str
    checked_on: str = "2026-08-23"


@dataclass(frozen=True)
class PrizePattern:
    """One exact winning condition for a standard game.

    `main_matches` and `supplementary_matches` are allowed exact match counts.
    `secondary_match` is used by a two-pool game such as Powerball.
    """

    main_matches: tuple[int, ...]
    supplementary_matches: tuple[int, ...] | None = None
    secondary_match: bool | None = None
    label: str = "prize"


@dataclass(frozen=True)
class GameDefinition:
    slug: str
    name: str
    operator: str
    mechanic: Mechanic
    jurisdictions: tuple[str, ...]
    schedule: str
    description: str
    sources: tuple[SourceRef, ...]
    pool_size: int | None = None
    ticket_pick: int | None = None
    winning_count: int | None = None
    supplementary_count: int = 0
    secondary_pool_size: int | None = None
    secondary_ticket_pick: int = 0
    ordered_positions: int | None = None
    radix: int | None = None
    draws_per_purchase: int = 1
    prize_patterns: tuple[PrizePattern, ...] = ()
    official_top_odds: int | None = None
    official_any_odds: float | None = None
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return asdict(self)


THE_LOTT_ODDS = SourceRef(
    "The Lott — odds of each game",
    "https://help.thelott.com/hc/en-us/articles/35525459564441-What-are-the-odds-of-each-game",
)
THE_LOTT_DRAW_SCHEDULE = SourceRef(
    "The Lott — current draw close schedule",
    "https://help.thelott.com/hc/en-us/articles/900000403663-Are-lottery-draws-still-being-conducted",
)
SATURDAY_RULES = SourceRef(
    "The Lott — Saturday Lotto rules overview",
    "https://help.thelott.com/hc/en-us/articles/4416859880985-How-do-I-play-the-Saturday-lotto-game",
)
WEEKDAY_RULES = SourceRef(
    "The Lott — Weekday Windfall rules overview",
    "https://help.thelott.com/hc/en-us/articles/34129397583513-How-do-I-play-the-Weekday-Windfall-game",
)
OZ_RULES = SourceRef(
    "The Lott — Oz Lotto rules overview",
    "https://help.thelott.com/hc/en-us/articles/4416863329689-How-do-I-play-the-Oz-Lotto-game",
)
POWERBALL_RULES = SourceRef(
    "The Lott — Powerball rules overview",
    "https://help.thelott.com/hc/en-us/articles/4416863320217-How-do-I-play-the-Powerball-game",
)
SET_FOR_LIFE_RULES = SourceRef(
    "The Lott — Set for Life rules overview",
    "https://help.thelott.com/hc/en-us/articles/4416859752601-How-do-I-play-the-Set-for-Life-game",
)
SUPER66_RULES = SourceRef(
    "The Lott — Super 66 rules overview",
    "https://help.thelott.com/hc/en-us/articles/4416863565465-How-do-I-play-the-Super-66-game",
)
STRIKE_RULES = SourceRef(
    "The Lott — Lotto Strike rules overview",
    "https://help.thelott.com/hc/en-us/articles/4416863538969-How-do-I-play-the-Lotto-Strike-game",
)
LUCKY_RULES = SourceRef(
    "The Lott — Lucky Lotteries rules overview",
    "https://help.thelott.com/hc/en-us/articles/4416872034073-How-do-I-play-the-Lucky-Lotteries-raffle-style-game",
)
KENO_RULES = SourceRef(
    "The Lott — Keno rules overview",
    "https://help.thelott.com/hc/en-us/articles/4416859934873-How-do-I-play-the-Keno-game",
)
THE_LOTT_GAMES = SourceRef(
    "The Lott — current games help catalog",
    "https://help.thelott.com/hc/en-us/sections/4416871363993-Games",
)
LOTTERYWEST_RESPONSIBLE = SourceRef(
    "Lotterywest — current top-prize odds and responsible play",
    "https://www.lotterywest.wa.gov.au/lotterywest/play-responsibly",
)
LOTTERYWEST_CASH3 = SourceRef(
    "Lotterywest — Cash 3 rules and odds",
    "https://www.lotterywest.wa.gov.au/games/cash-3",
)
LOTTERYWEST_MEDLEY = SourceRef(
    "Lotterywest — Millionaire Medley rules and odds",
    "https://www.lotterywest.wa.gov.au/games/millionaire-medley",
)
LOTTERYWEST_POWERBALL = SourceRef(
    "Lotterywest — Powerball division patterns and odds",
    "https://www.lotterywest.wa.gov.au/games/powerball",
)
LOTTERYWEST_OZ = SourceRef(
    "Lotterywest — Oz Lotto division patterns and odds",
    "https://www.lotterywest.wa.gov.au/games/oz-lotto",
)
LOTTERYWEST_SET_FOR_LIFE = SourceRef(
    "Lotterywest — Set for Life division patterns and odds",
    "https://www.lotterywest.wa.gov.au/games/set-for-life",
)


SATURDAY_PRIZES = (
    PrizePattern((6,), label="Division 1"),
    PrizePattern((5,), (1, 2), label="Division 2"),
    PrizePattern((5,), (0,), label="Division 3"),
    PrizePattern((4,), label="Division 4"),
    PrizePattern((3,), (1, 2), label="Division 5"),
    PrizePattern((3,), (0,), label="Division 6"),
)

MILLIONAIRE_MEDLEY_PRIZES = (
    PrizePattern((6,), label="Division 1"),
    PrizePattern((5,), (1, 2), label="Division 2"),
    PrizePattern((5,), (0,), label="Division 3"),
    PrizePattern((4,), label="Division 4"),
    PrizePattern((3,), (1, 2), label="Division 5"),
    PrizePattern((1, 2), (2,), label="Division 6"),
)

OZ_PRIZES = (
    PrizePattern((7,), label="Division 1"),
    PrizePattern((6,), (1, 2, 3), label="Division 2"),
    PrizePattern((6,), (0,), label="Division 3"),
    PrizePattern((5,), (1, 2), label="Division 4"),
    PrizePattern((5,), (0,), label="Division 5"),
    PrizePattern((4,), label="Division 6"),
    PrizePattern((3,), (1, 2, 3), label="Division 7"),
)

SET_FOR_LIFE_PRIZES = (
    PrizePattern((7,), label="Division 1"),
    PrizePattern((6,), (1, 2), label="Division 2"),
    PrizePattern((6,), (0,), label="Division 3"),
    PrizePattern((5,), (1, 2), label="Division 4"),
    PrizePattern((5,), (0,), label="Division 5"),
    PrizePattern((4,), (1, 2), label="Division 6"),
    PrizePattern((4,), (0,), label="Division 7"),
    PrizePattern((3,), (1, 2), label="Division 8"),
)

POWERBALL_PRIZES = (
    PrizePattern((7,), secondary_match=True, label="Division 1"),
    PrizePattern((7,), secondary_match=False, label="Division 2"),
    PrizePattern((6,), secondary_match=True, label="Division 3"),
    PrizePattern((6,), secondary_match=False, label="Division 4"),
    PrizePattern((5,), secondary_match=True, label="Division 5"),
    PrizePattern((4,), secondary_match=True, label="Division 6"),
    PrizePattern((5,), secondary_match=False, label="Division 7"),
    PrizePattern((3,), secondary_match=True, label="Division 8"),
    PrizePattern((2,), secondary_match=True, label="Division 9"),
)


GAMES: dict[str, GameDefinition] = {
    "saturday-lotto": GameDefinition(
        slug="saturday-lotto",
        name="Saturday Lotto / TattsLotto",
        operator="The Lott",
        mechanic="one-pool",
        jurisdictions=("QLD", "NSW", "ACT", "VIC", "TAS", "SA", "NT"),
        schedule="Saturday",
        description="Choose 6 from 45; six winning and two supplementary numbers are drawn.",
        sources=(SATURDAY_RULES, THE_LOTT_ODDS, THE_LOTT_DRAW_SCHEDULE),
        pool_size=45,
        ticket_pick=6,
        winning_count=6,
        supplementary_count=2,
        prize_patterns=SATURDAY_PRIZES,
        official_top_odds=8_145_060,
        official_any_odds=42.0,
    ),
    "weekday-windfall": GameDefinition(
        slug="weekday-windfall",
        name="Weekday Windfall",
        operator="The Lott",
        mechanic="one-pool",
        jurisdictions=("QLD", "NSW", "ACT", "VIC", "TAS", "SA", "NT"),
        schedule="Monday, Wednesday, Friday",
        description="Choose 6 from 45; six winning and two supplementary numbers are drawn.",
        sources=(WEEKDAY_RULES, THE_LOTT_ODDS, THE_LOTT_DRAW_SCHEDULE),
        pool_size=45,
        ticket_pick=6,
        winning_count=6,
        supplementary_count=2,
        official_top_odds=8_145_060,
        official_any_odds=86.0,
        notes=(
            "The current help overview verifies the 6/45 mechanic and Division 1. Full lower-division "
            "patterns are not inferred here; the official reported any-prize odds remain metadata.",
        ),
    ),
    "oz-lotto": GameDefinition(
        slug="oz-lotto",
        name="Oz Lotto",
        operator="The Lott",
        mechanic="one-pool",
        jurisdictions=("QLD", "NSW", "ACT", "VIC", "TAS", "SA", "NT", "WA"),
        schedule="Tuesday",
        description="Choose 7 from 47; seven winning and three supplementary numbers are drawn.",
        sources=(OZ_RULES, LOTTERYWEST_OZ, THE_LOTT_ODDS),
        pool_size=47,
        ticket_pick=7,
        winning_count=7,
        supplementary_count=3,
        prize_patterns=OZ_PRIZES,
        official_top_odds=62_891_499,
        official_any_odds=51.0,
    ),
    "powerball": GameDefinition(
        slug="powerball",
        name="Powerball",
        operator="The Lott",
        mechanic="two-pool",
        jurisdictions=("QLD", "NSW", "ACT", "VIC", "TAS", "SA", "NT", "WA"),
        schedule="Thursday",
        description="Choose 7 from 35 plus one Powerball from a separate pool of 20.",
        sources=(POWERBALL_RULES, LOTTERYWEST_POWERBALL, THE_LOTT_ODDS),
        pool_size=35,
        ticket_pick=7,
        winning_count=7,
        secondary_pool_size=20,
        secondary_ticket_pick=1,
        prize_patterns=POWERBALL_PRIZES,
        official_top_odds=134_490_400,
        official_any_odds=44.0,
    ),
    "set-for-life": GameDefinition(
        slug="set-for-life",
        name="Set for Life",
        operator="The Lott",
        mechanic="one-pool",
        jurisdictions=("QLD", "NSW", "ACT", "VIC", "TAS", "SA", "NT", "WA"),
        schedule="Daily; a standard purchase covers seven consecutive draws",
        description="Choose 7 from 44; seven winning and two supplementary numbers are drawn daily.",
        sources=(SET_FOR_LIFE_RULES, LOTTERYWEST_SET_FOR_LIFE, THE_LOTT_ODDS),
        pool_size=44,
        ticket_pick=7,
        winning_count=7,
        supplementary_count=2,
        draws_per_purchase=7,
        prize_patterns=SET_FOR_LIFE_PRIZES,
        official_top_odds=38_320_568,
        official_any_odds=51.0,
        notes=(
            "Official standard-game odds are per draw. The catalog also computes the cumulative chance "
            "over the seven consecutive independent draws included in a standard purchase.",
        ),
    ),
    "super-66": GameDefinition(
        slug="super-66",
        name="Super 66",
        operator="The Lott",
        mechanic="ordered-digits",
        jurisdictions=("QLD", "VIC", "TAS", "SA", "NT", "WA"),
        schedule="Saturday",
        description="Six ordered digits are drawn independently from six 0–9 barrels.",
        sources=(SUPER66_RULES, THE_LOTT_ODDS, THE_LOTT_DRAW_SCHEDULE),
        ordered_positions=6,
        radix=10,
        official_top_odds=1_000_000,
        official_any_odds=51.0,
    ),
    "lotto-strike": GameDefinition(
        slug="lotto-strike",
        name="Lotto Strike",
        operator="The Lott",
        mechanic="ordered-without-replacement",
        jurisdictions=("NSW", "ACT"),
        schedule="Monday, Wednesday, Friday, Saturday; add-on to corresponding Lotto draw",
        description="Choose four ordered numbers; they must match the first four Lotto balls in position.",
        sources=(STRIKE_RULES, THE_LOTT_ODDS, THE_LOTT_DRAW_SCHEDULE),
        pool_size=45,
        ordered_positions=4,
        official_top_odds=3_575_880,
        official_any_odds=11.0,
    ),
    "lucky-lotteries-super": GameDefinition(
        slug="lucky-lotteries-super",
        name="Lucky Lotteries Super Jackpot",
        operator="The Lott",
        mechanic="raffle",
        jurisdictions=("QLD", "NSW", "ACT", "VIC", "TAS", "SA", "NT"),
        schedule="Draw closes when the ticket pool sells out",
        description="Finite raffle-style ticket pool with a cash-prize draw and a separate jackpot draw.",
        sources=(LUCKY_RULES, THE_LOTT_ODDS),
        official_top_odds=18_385_877,
        official_any_odds=24.0,
        notes=("Jackpot odds are operator-reported; this is not modelled as a combination-selection game.",),
    ),
    "lucky-lotteries-mega": GameDefinition(
        slug="lucky-lotteries-mega",
        name="Lucky Lotteries Mega Jackpot",
        operator="The Lott",
        mechanic="raffle",
        jurisdictions=("QLD", "NSW", "ACT", "VIC", "TAS", "SA", "NT"),
        schedule="Draw closes when the ticket pool sells out",
        description="Finite raffle-style ticket pool with a cash-prize draw and a separate jackpot draw.",
        sources=(LUCKY_RULES, THE_LOTT_ODDS),
        official_top_odds=9_483_168,
        official_any_odds=17.0,
        notes=("Jackpot odds are operator-reported; this is not modelled as a combination-selection game.",),
    ),
    "keno-sa": GameDefinition(
        slug="keno-sa",
        name="Keno (SA through The Lott)",
        operator="The Lott",
        mechanic="keno",
        jurisdictions=("SA",),
        schedule="Every few minutes",
        description="20 numbers are drawn from 80; Keno Single lets players select Spot 1 through Spot 10.",
        sources=(KENO_RULES, THE_LOTT_GAMES),
        pool_size=80,
        winning_count=20,
        notes=(
            "There is no single universal top-prize denominator across all Keno spot sizes. Use the exact "
            "spot match calculator instead.",
        ),
    ),
    "instant-scratch-its": GameDefinition(
        slug="instant-scratch-its",
        name="Instant Scratch-Its",
        operator="The Lott",
        mechanic="variable-instant",
        jurisdictions=("QLD", "NSW", "ACT", "VIC", "TAS", "SA", "NT"),
        schedule="Instant product family",
        description="Scratch-ticket mechanics and top-prize odds vary by the specific printed game.",
        sources=(THE_LOTT_ODDS,),
        official_any_odds=4.0,
        notes=(
            "The operator reports roughly 1 in 4 for any prize across the product family, while top-prize "
            "odds must be read from the specific ticket. Do not compare this as a single fixed lottery.",
        ),
    ),
    "play-for-purpose": GameDefinition(
        slug="play-for-purpose",
        name="Play For Purpose charity raffle",
        operator="Play For Purpose / The Lott platform",
        mechanic="variable-raffle",
        jurisdictions=("Australia — subject to raffle terms",),
        schedule="Raffle draw schedule varies",
        description="Charity raffle whose winning odds depend on the number of tickets sold in that draw.",
        sources=(THE_LOTT_ODDS,),
        notes=("No fixed odds are hard-coded because the operator states they depend on ticket sales.",),
    ),
    "millionaire-medley": GameDefinition(
        slug="millionaire-medley",
        name="Millionaire Medley",
        operator="Lotterywest",
        mechanic="one-pool",
        jurisdictions=("WA",),
        schedule="Monday, Wednesday, Friday",
        description="WA draw: choose 6 from 45; six winning and two supplementary numbers are drawn.",
        sources=(LOTTERYWEST_MEDLEY, LOTTERYWEST_RESPONSIBLE),
        pool_size=45,
        ticket_pick=6,
        winning_count=6,
        supplementary_count=2,
        prize_patterns=MILLIONAIRE_MEDLEY_PRIZES,
        official_top_odds=8_145_060,
        official_any_odds=86.0,
        notes=(
            "The draw mechanism matches the 6/45 Lotto family, but the lower-division prize mapping is "
            "different from Saturday Lotto. This is why draw mechanics and prize rules are separate.",
        ),
    ),
    "cash-3": GameDefinition(
        slug="cash-3",
        name="Cash 3",
        operator="Lotterywest",
        mechanic="ordered-digits",
        jurisdictions=("WA",),
        schedule="Daily",
        description="Three digits 0–9 are drawn; Exact Order, Any Order and Both Ways play types are offered.",
        sources=(LOTTERYWEST_CASH3, LOTTERYWEST_RESPONSIBLE),
        ordered_positions=3,
        radix=10,
        official_top_odds=1_000,
        notes=(
            "The computed 1-in-1,000 value is for Exact Order. Any Order odds depend on whether the chosen "
            "multiset has 3 or 6 distinct permutations.",
        ),
    ),
    "scratch-n-win": GameDefinition(
        slug="scratch-n-win",
        name="Scratch'n'Win",
        operator="Lotterywest",
        mechanic="variable-instant",
        jurisdictions=("WA",),
        schedule="Instant product family",
        description="WA scratch-ticket family; prize tables and odds vary by ticket design/print run.",
        sources=(LOTTERYWEST_RESPONSIBLE,),
        notes=("No universal top-prize odds are assigned to a variable printed-ticket family.",),
    ),
}


def get_game(slug: str) -> GameDefinition:
    try:
        return GAMES[slug]
    except KeyError as exc:
        raise KeyError(f"unknown game: {slug}") from exc


def list_games(*, operator: str | None = None, mechanic: Mechanic | None = None) -> list[GameDefinition]:
    games = list(GAMES.values())
    if operator is not None:
        games = [game for game in games if game.operator.casefold() == operator.casefold()]
    if mechanic is not None:
        games = [game for game in games if game.mechanic == mechanic]
    return sorted(games, key=lambda game: (game.operator, game.name))
