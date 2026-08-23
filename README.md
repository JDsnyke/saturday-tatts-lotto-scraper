# Australian Lottery Probability Lab

An open-source Australian lottery research project focused on **exact probability, sourced game mechanics, multi-entry portfolio structure, data quality and honest uncertainty**.

Saturday Lotto / TattsLotto remains the deepest research module, including exact fixed-portfolio probability and validated portfolio optimisation. Version 3 adds a reusable game-definition layer so materially different products such as Powerball, Oz Lotto, Set for Life, Super 66, Lotto Strike, Keno, Lotterywest Cash 3 and charity art unions are not forced into Saturday-specific mathematics.

The project deliberately does **not** claim that hot, cold, overdue, recently drawn or historically common numbers are more likely in the next fair draw.

## v3.0.0 — multi-game foundation

### Sourced game catalog

The Games & Odds Lab models distinct probability families and keeps operator/jurisdiction provenance visible:

- **one-pool combination draws** — Saturday Lotto, Weekday Windfall, Oz Lotto, Set for Life and Lotterywest Millionaire Medley;
- **two-pool draws** — Powerball;
- **ordered digits** — Super 66 and Lotterywest Cash 3;
- **ordered sampling without replacement** — Lotto Strike;
- **Keno / hypergeometric** — South Australian Keno through The Lott;
- **raffle-style products** — Lucky Lotteries;
- **variable instant / raffle families** — Instant Scratch-Its, Scratch'n'Win, Play For Purpose and sourced Australian charity/art-union alternatives.

Current alternative snapshots include yourtown Prize Home, Mater Prize Home, Mater Cars for Cancer, Dream Home Art Union / RSL Queensland, Endeavour Foundation Prize Home and Endeavour Pay Day.

See [`docs/GAME_CATALOG.md`](docs/GAME_CATALOG.md) for the evidence taxonomy and source policy.

### Exact probability engines

Where current mechanics and prize conditions support exact calculation, the engine derives rather than guesses:

```text
Saturday / Weekday / Millionaire Medley top combination count = C(45,6) = 8,145,060
Oz Lotto Division 1                                  = C(47,7) = 62,891,499
Powerball Division 1                                 = C(35,7) × 20 = 134,490,400
Set for Life Division 1 per draw                     = C(44,7) = 38,320,568
Super 66 Division 1                                  = 10^6 = 1,000,000
Lotto Strike Division 1                              = 45P4 = 3,575,880
Cash 3 Exact Order                                   = 10^3 = 1,000
```

Keno Spot matches use the exact hypergeometric distribution for 20 balls drawn from 80. Cash 3 Any Order accounts for the number of distinct permutations in the chosen three-digit multiset.

### Exact vs reported vs variable

The public catalog distinguishes three evidence states:

1. **Computed / exact** — follows from a verified mathematical mechanism.
2. **Operator-reported** — current operator odds are retained as metadata where the full mechanism is not independently derived.
3. **Variable / draw-specific** — no fixed denominator is invented for products whose odds depend on valid entries, tickets sold, bundle bonuses, print runs or draw-specific terms.

A raffle's maximum ticket or entry capacity is **not automatically exact one-ticket odds**. For example, yourtown explicitly states First Prize odds depend on tickets sold, while Mater Prize Home bundles can materially change total entries.

Public aggregate any-prize figures are currently withheld for Weekday Windfall, Lotto Strike and both Lucky Lotteries jackpot products where a current aggregate figure was not independently re-verified during the v3 source audit. Their verified top/jackpot information is retained.

### One web data source

Python definitions are authoritative. The static web catalog is generated with:

```bash
PYTHONPATH=src python -m lotto_lab game-catalog-json --output assets/game_catalog.json
```

`assets/games.js` fetches that generated JSON rather than embedding a second odds table. The dedicated catalog workflow regenerates the asset and fails if parsed content diverges.

## Saturday Lotto probability and portfolio research

For the current 6-from-45 Saturday game there are exactly:

```text
C(45,6) = 8,145,060
```

One standard game therefore has Division 1 probability `1 / 8,145,060`. For a fixed number of **distinct** standard games, choosing different numbers cannot improve Division 1 probability in a fair draw.

The useful fixed-budget portfolio question is lower-tier overlap. The project separates:

- owning more distinct combinations — the direct Division 1 probability lever, with higher spend;
- reducing redundant overlap between a fixed number of entries;
- conditional prize-sharing / crowding research, which does **not** change draw probability.

### Exact any-prize evaluator

For a fixed Saturday portfolio, v2.1.3 computes the exact probability that at least one game reaches three or more winning main numbers. It uses complement dynamic programming rather than Monte Carlo or enumerating all 8,145,060 outcomes individually.

The larger fixed 10-game benchmark found mean exact any-prize probabilities of:

| Strategy | Exact mean any-prize probability |
| --- | ---: |
| Coverage | **23.00372595%** |
| Any-prize-bound | 23.00482171% |
| Division-4-bound | 23.00703433% |
| QuickPick | **21.44444742%** |

Coverage vs QuickPick was about **+1.5593 percentage points** in that fixed benchmark, with a portfolio-seed bootstrap 95% interval of about **+1.4769 to +1.6505 points** and empirical probability-of-superiority `1.000`. This is a lower-tier portfolio-diversification result, not a Division 1 or prediction edge.

### Exact-local refinement

v2.1.4 adds an optional higher-compute local search on top of Coverage. It screens one-number swaps cheaply, then accepts a mutation **only** when the full exact evaluator proves that the integer number of any-prize winning-main sets increases. Existing certified Division-4-or-better global optimality is preserved by default.

The frozen release search budget is:

```text
2 search passes
4 bound-ranked exact candidates per pass
1 deterministic exploration candidate per pass
```

Independent confirmation on 16 new 10-game Coverage portfolios rooted at seed `20260823` found 11 improvements, 5 unchanged and 0 worsened, with mean exact any-prize improvement about **+0.001126 percentage points**. Coverage remains the fast balanced default; `exact-local` is an optional non-worsening local refinement, not proof of a global optimum.

## Web application

The static GitHub Pages application includes:

- **Games & Odds Lab** — operator/mechanic/jurisdiction catalog plus Set for Life, Keno and Cash 3 calculators;
- **Saturday Probability Planner** — games × repeated draws;
- **Saturday Ticket Lab** — Coverage, QuickPick and experimental anti-crowding modes;
- exact Saturday prize/match probability views and System-entry equivalence;
- exact fixed-portfolio any-prize probability and probability certificates;
- multi-seed Benchmark Lab;
- historical Draw Explorer and descriptive diagnostics;
- data provenance/freshness status;
- share/export tools;
- PWA/offline caching.

No server runtime or browser framework is required.

## CLI

Install development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Multi-game examples:

```bash
PYTHONPATH=src python -m lotto_lab games
PYTHONPATH=src python -m lotto_lab games --operator 'The Lott' --json
PYTHONPATH=src python -m lotto_lab game-odds --game powerball
PYTHONPATH=src python -m lotto_lab game-odds --game mater-prize-home
PYTHONPATH=src python -m lotto_lab game-catalog-json
PYTHONPATH=src python -m lotto_lab keno --spot 10
PYTHONPATH=src python -m lotto_lab cash3 --digits 223
```

Saturday examples:

```bash
PYTHONPATH=src python -m lotto_lab validate
PYTHONPATH=src python -m lotto_lab stats
PYTHONPATH=src python -m lotto_lab tickets --count 10 --mode coverage
PYTHONPATH=src python -m lotto_lab tickets --count 10 --mode exact-local --json
PYTHONPATH=src python -m lotto_lab exact-any-prize --count 10 --mode coverage
PYTHONPATH=src python -m lotto_lab optimize-any-prize --count 10 --seed exact-local-example
PYTHONPATH=src python -m lotto_lab benchmark-exact-objectives --count 10 --portfolios 32 --random-portfolios 128
PYTHONPATH=src python -m lotto_lab benchmark-local-search --count 10 --portfolios 16 --seed 20260823
PYTHONPATH=src python -m lotto_lab verify-secondary --latest 10
```

## Data and release gates

The Saturday results refresh remains independently verified before generated data assets are published. v3 adds a separate multi-game source/catalog gate; the game catalog is not currently a historical-results scraper for every product.

CI covers:

- Ruff and Python compilation;
- full unit suite;
- Saturday dataset/stat/provenance regeneration;
- exact Saturday objective benchmarks;
- multi-game exact denominator/distribution tests;
- current alternative raffle snapshot regressions;
- canonical game-catalog regeneration and tracked-asset equality;
- browser JavaScript syntax and static-site/PWA references.

## Responsible-use note

Lottery products are entertainment, not investments. Easier top-prize odds do not by themselves imply better expected value. Meaningful value comparison needs the **same product/draw's** ticket price, prize amounts, payout rules, sharing rules, annuity terms and valid-entry/prize inventory.

More entries generally mean more spend. The project does not recommend increasing a lottery budget.

## Documentation

- [`ROADMAP.md`](ROADMAP.md)
- [`docs/GAME_CATALOG.md`](docs/GAME_CATALOG.md)
- [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md)
- [`docs/ODDS_OPTIMISATION.md`](docs/ODDS_OPTIMISATION.md)
- [`docs/BENCHMARKING.md`](docs/BENCHMARKING.md)
- [`docs/EXACT_ANY_PRIZE.md`](docs/EXACT_ANY_PRIZE.md)
- [`CONTRIBUTING.md`](CONTRIBUTING.md)
- [`GITHUB_PAGES.md`](GITHUB_PAGES.md)

Operator rules and draw-specific raffle terms can change. Source-stamped catalog facts should always be rechecked before relying on a future release.
