# Australian game catalog methodology

Version 3 separates **the probability experiment** from **the prize mapping** and from **operator-reported commercial metadata**. This prevents a 6/45 Lotto game, Powerball, Keno, an ordered-digit game and a charity art union from being pushed through the same formula merely because each advertises odds as `1 in X`.

## Evidence labels

### Computed / exact

A value is computed when the current sourced game mechanism is sufficient to derive it combinatorially.

Examples:

- Saturday Lotto / Weekday Windfall: `C(45,6) = 8,145,060` top combinations;
- Oz Lotto: `C(47,7) = 62,891,499`;
- Powerball: `C(35,7) × 20 = 134,490,400`;
- Set for Life: `C(44,7) = 38,320,568` per draw;
- Super 66: `10^6 = 1,000,000` ordered six-digit outcomes;
- Lotto Strike: `45P4 = 3,575,880` ordered first-four outcomes;
- Lotterywest Cash 3 Exact Order: `10^3 = 1,000` ordered three-digit outcomes;
- Keno Spot matches: hypergeometric probabilities for 20 numbers drawn from 80.

Where complete current prize conditions are sourced, the engine also maps exact match states into prize divisions and computes exact standard-game any-prize probability.

### Operator-reported

Some values are published by the operator but are not independently derived from the currently modelled experiment. These are retained as reported metadata only.

Lucky Lotteries is the main example: it is a raffle-style game with a cash-prize draw and separate jackpot process, so its current jackpot odds are not represented as a fake choose-k combination formula.

### Variable / draw-specific

A fixed odds denominator is intentionally omitted when it depends on the particular draw, ticket print run, number of valid entries, bundle structure or sales outcome.

Examples include:

- charity Prize Home / art-union draws;
- Play For Purpose;
- Instant Scratch-Its and Scratch'n'Win product families;
- any raffle where the operator says odds depend on tickets sold.

A published **maximum ticket or entry capacity is not automatically exact one-ticket odds**. The final denominator may depend on actual valid entries, bonus-entry bundles, unsold tickets or the specific draw terms.

## Current catalog families

### The Lott

- Saturday Lotto / TattsLotto
- Weekday Windfall
- Oz Lotto
- Powerball
- Set for Life
- Super 66
- Lotto Strike
- Lucky Lotteries Super Jackpot
- Lucky Lotteries Mega Jackpot
- Keno in South Australia
- Instant Scratch-Its
- Play For Purpose

### Lotterywest / Western Australia

- Millionaire Medley
- Cash 3
- Scratch'n'Win

National games sold by Lotterywest are also used as independent current sources for division conditions where appropriate.

### Australian charity / art-union alternatives

The catalog currently includes sourced snapshots for:

- yourtown Prize Home Draws;
- Mater Prize Home;
- Mater Cars for Cancer;
- Dream Home Art Union / RSL Queensland;
- Endeavour Foundation Prize Home;
- Endeavour Pay Day.

These are deliberately catalogued as `variable-raffle`, not ranked as though a current ticket cap were a guaranteed final odds denominator.

## Current source snapshots

Source facts are stamped `checked_on = 2026-08-23` in the Python definitions and the generated public catalog.

Examples of draw-specific snapshots retained for auditability include:

- Mater Prize Home 327: draw 23 October 2026; close 20 October 2026; tickets from $2; possible entry range 13,455,147–22,805,334 because bundles alter total entries;
- Mater Cars for Cancer 130: draw 16 September 2026; close 13 September 2026; $30 tickets; maximum 85,117 tickets;
- Endeavour Pay Day 221: draw 8 October 2026; $5 tickets; maximum 200,000 tickets. No sales-close date is stored because a current authoritative sales-close date was not established during the source check;
- yourtown: most Prize Home draws have 500,000 tickets available, while First Prize odds are explicitly stated to depend on tickets actually sold.

When a fact cannot be current-source verified, the project removes or masks it instead of carrying an older number forward. Public aggregate any-prize odds are currently masked for Weekday Windfall, Lotto Strike and both Lucky Lotteries jackpot products until those aggregate figures are re-verified from a current authoritative source.

## One source of truth for the web

The Python game definitions are authoritative. The command:

```bash
PYTHONPATH=src python -m lotto_lab game-catalog-json --output assets/game_catalog.json
```

generates the static web catalog. `assets/games.js` fetches that file; it does not contain a second hard-coded odds table.

The dedicated `Multi-game catalog` GitHub Actions workflow regenerates the JSON and compares its parsed content with the tracked asset. A Python definition can therefore not change without the static web catalog being regenerated as well.

## CLI

```bash
PYTHONPATH=src python -m lotto_lab games
PYTHONPATH=src python -m lotto_lab games --operator 'The Lott' --json
PYTHONPATH=src python -m lotto_lab game-odds --game powerball
PYTHONPATH=src python -m lotto_lab game-catalog-json
PYTHONPATH=src python -m lotto_lab keno --spot 10
PYTHONPATH=src python -m lotto_lab cash3 --digits 223
```

## What v3 does not claim

- It does not rank future numbers using historical frequency, recency, hot/cold or overdue status.
- It does not say an easier jackpot denominator means better expected value.
- It does not treat a maximum raffle ticket supply as final exact odds unless the draw mechanics justify that equality.
- It does not compare a seven-draw Set for Life purchase with a single-draw ticket without identifying the repeated independent draw exposure.
- It does not apply the Saturday Lotto portfolio optimiser to Powerball, Oz Lotto, Keno or raffle products before a game-specific objective and validation method exist.
- It does not include offshore lottery-reseller products as Australian alternatives.

## Next research layer

The reusable catalog makes game-specific portfolio research possible without conflating mechanics. Candidate future work includes:

- exact multi-entry union objectives for Oz Lotto and Set for Life;
- a two-pool Powerball portfolio objective that accounts separately for main selections and Powerball choices;
- ordered-prefix/suffix portfolio mathematics for Super 66 and position-aware Lotto Strike analysis;
- Keno prize-condition models by supported Spot size and jurisdiction;
- automated operator-rule/snapshot refresh with provenance checks;
- expected-value tooling only when ticket cost, prize amounts, sharing rules and payout inputs are all sourced for the same draw/product.
