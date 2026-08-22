# Saturday Lotto Probability Lab

An open-source Saturday Lotto / TattsLotto research project focused on **exact probability, data quality, multi-entry portfolio structure and honest uncertainty**.

The project deliberately does **not** claim that hot, cold, overdue, recently drawn or historically common numbers are more likely in the next fair draw.

## What can actually improve?

For the current 6-from-45 game there are exactly:

```text
C(45, 6) = 8,145,060
```

possible standard six-number combinations. Therefore one standard game has Division 1 probability `1 / 8,145,060`, while `n` distinct standard games have probability `n / 8,145,060` in one draw.

Number selection cannot improve that Division 1 probability if the draw is fair. Objective optimisation instead falls into three separate categories:

1. **Own more distinct combinations** — the only direct Division 1 probability increase.
2. **Reduce portfolio redundancy** — structure multiple games so their lower-tier winning events overlap less.
3. **Conditional prize-sharing research** — experimentally avoid patterns people may choose disproportionately. This does not improve the chance of being drawn; it may matter only to how many people share a pari-mutuel prize if that combination wins.

See [`docs/ODDS_OPTIMISATION.md`](docs/ODDS_OPTIMISATION.md), [`docs/BENCHMARKING.md`](docs/BENCHMARKING.md) and [`docs/EXACT_ANY_PRIZE.md`](docs/EXACT_ANY_PRIZE.md) for the claim hierarchy and limitations.

## v2.1.3 highlights

### Exact fixed-portfolio any-prize probability

Under the current Saturday Lotto prize structure, matching at least three of the six winning main numbers is sufficient to win some prize division. v2.1.3 therefore computes the exact probability that **at least one game in a fixed portfolio reaches three or more main matches**.

It does this without Monte Carlo and without iterating over all 8,145,060 winning sets individually.

The evaluator counts the complementary event with dynamic programming:

```text
no prize = every portfolio ticket finishes with 0, 1 or 2 main matches

exact any-prize probability
  = 1 - no-prize winning-main sets / C(45,6)
```

Each ticket's surviving match count is encoded as a base-3 digit. Selecting a ball transition is discarded as soon as it would give any ticket its third match. All state weights and final favourable-set counts are integers.

The evaluator is deliberately opt-in and capped at 12 tickets by default so ordinary ticket metrics and data refreshes do not inherit an unexpected large workload.

### Exact confirmation benchmark

The larger v2.1.3 confirmation benchmark evaluates **true combinatorial any-prize probability**, not simulated hit rates:

- 10 games per portfolio;
- 32 independently seeded Coverage portfolios;
- 32 Any-prize-bound portfolios;
- 32 Division-4-bound portfolios;
- 128 independently seeded uniform QuickPick portfolios;
- root seed `20260822`;
- 320 candidate games per greedy construction step;
- 2,000 bootstrap resamples across portfolio-generator seeds.

Mean exact any-prize probabilities:

| Strategy | Exact mean any-prize probability |
| --- | ---: |
| Coverage | **23.00372595%** |
| Any-prize-bound | 23.00482171% |
| Division-4-bound | 23.00703433% |
| QuickPick | **21.44444742%** |

The key result is **Coverage vs QuickPick**:

- exact mean advantage: about **+1.5593 percentage points**;
- portfolio-seed bootstrap 95% interval: about **+1.4769 to +1.6505 points**;
- probability-of-superiority: **1.000** in this fixed benchmark — every tested Coverage portfolio had a higher exact any-prize probability than every tested QuickPick portfolio.

This is a lower-tier **portfolio diversification** result. It does not make any individual six-number combination more likely to be drawn, and same-sized sets of distinct games still have identical Division 1 probability.

Neither specialist generator demonstrated a reliable exact any-prize advantage over Coverage in the larger confirmation distribution:

- Any-prize-bound vs Coverage: about **+0.00110 points**, 95% interval **−0.00506 to +0.00721 points**;
- Division-4-bound vs Coverage: about **+0.00331 points**, 95% interval **−0.00168 to +0.00869 points**.

A smaller initial 12-seed exact benchmark had favoured Any-prize-bound, but that ordering did not remain convincing in the larger confirmation run. The project records both results rather than cherry-picking the smaller favourable sample.

**Coverage therefore remains the recommended balanced default.**

### Exact portfolio certificates

v2.1.2 added exact two-ticket event-intersection combinatorics and portfolio certificates.

For portfolio events `Ai`:

```text
S1 = sum P(Ai)
S2 = sum P(Ai ∩ Aj)

P(any event) >= max(0, S1 - S2)
```

That second-order Bonferroni result remains a cheap, rigorous lower bound and a useful construction objective. v2.1.3 adds the exact any-prize union for smaller fixed portfolios, so the bound is no longer presented as the best available answer when exact evaluation is practical.

For **Division 4 or better**, there is a stronger theorem. If every pair of six-number games shares at most one number, two games cannot both match four or more of the same six winning main numbers. Their `>=4 main` events are pairwise disjoint, so:

```text
P(Division 4 or better somewhere in portfolio)
  = ticket_count × P(one game matches >=4 main)
```

That reaches the universal sum-of-marginals upper bound, so the portfolio is globally optimal for Division 4-or-better probability at that ticket count.

### Separate ticket objectives

The CLI keeps objectives explicit instead of pretending one heuristic is universally best:

- `coverage` — generic quadruple → triple → pair subset diversity; **recommended balanced default**;
- `any-prize-bound` — greedily minimises exact pairwise `>=3 main` event-intersection cost;
- `division4-bound` — minimises exact pairwise `>=4 main` event intersections and can return a global-optimality certificate;
- `random` — uniform QuickPick baseline;
- `anti-crowding` — experimental conditional prize-sharing research only.

Anti-crowding is intentionally excluded from the exact draw-probability comparison command because it addresses a different question: conditional co-winner risk, not the probability that numbers are drawn.

### A rejected optimiser is also a result

A prototype trained ticket selection directly on simulated any-prize outcomes. It performed strongly on its training sample but failed to improve on the structural baseline on held-out draws.

That sampled-training optimiser is **not shipped as a recommended strategy**. The negative result is retained so training-sample noise is not later reintroduced as an apparent lottery edge.

### Probability engine

The Python engine now includes:

- exact Division 1 combination count and multi-game probability;
- cumulative probability across repeated independent draws;
- System 6–20 equivalence via `C(k, 6)` standard combinations;
- exact 0–6 main-number match distribution;
- exact Division 1–6 standard-game probabilities;
- exact standard-game any-prize probability;
- exact two-ticket `>=k main` event-intersection probabilities;
- rigorous Bonferroni portfolio lower bounds;
- exact pairwise-disjoint Division-4+ certificates;
- **exact fixed-portfolio any-prize union probability** via complement dynamic programming.

### Data integrity

- strict CSV validation;
- primary scraper plus independent secondary-source comparison for newest draws;
- draw-number/source-link capture from the secondary source;
- SHA-256 provenance for both historical CSV files;
- saved scraper fixtures for markup-regression tests;
- scheduled refresh refuses to publish new data when secondary verification fails;
- migration-aware refresh rebuilds old schema assets even when the CSV itself did not change.

### Web application

The GitHub Pages site includes:

- Probability Planner for games × repeated draws;
- System 6–20 calculator;
- exact prize-division table;
- main-match distribution;
- Ticket Lab with coverage, QuickPick and experimental anti-crowding modes;
- pair/triple/quadruple coverage metrics;
- local exploratory portfolio simulation;
- shareable ticket-set URLs and CSV export;
- Strategy Evidence view;
- Draw Explorer with date/search/number filters and CSV export;
- accessible keyboard frequency chart;
- data freshness and provenance display;
- dedicated Benchmark Lab with client-side multi-seed exploratory runs;
- **exact any-prize probability for the generated 10-game reference Coverage portfolio**;
- Bonferroni and Division-4 certificates shown separately from simulations;
- system/light/dark themes;
- offline/PWA cache support.

No browser framework or server runtime is required: the published dashboard remains a static GitHub Pages application.

## CLI

Install dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Examples:

```bash
PYTHONPATH=src python -m lotto_lab validate
PYTHONPATH=src python -m lotto_lab stats

PYTHONPATH=src python -m lotto_lab tickets --count 10 --mode coverage
PYTHONPATH=src python -m lotto_lab tickets --count 10 --mode any-prize-bound --json
PYTHONPATH=src python -m lotto_lab tickets --count 10 --mode division4-bound --json
PYTHONPATH=src python -m lotto_lab tickets --count 10 --mode random
PYTHONPATH=src python -m lotto_lab tickets --count 10 --mode anti-crowding

PYTHONPATH=src python -m lotto_lab exact-any-prize --count 10 --mode coverage
PYTHONPATH=src python -m lotto_lab exact-any-prize --count 10 --mode any-prize-bound

PYTHONPATH=src python -m lotto_lab simulate --count 10 --trials 50000
PYTHONPATH=src python -m lotto_lab benchmark --count 10 --coverage-portfolios 50 --random-portfolios 200 --trials 5000
PYTHONPATH=src python -m lotto_lab benchmark-objectives --count 10 --portfolios 24 --random-portfolios 96 --trials 5000
PYTHONPATH=src python -m lotto_lab benchmark-exact-objectives --count 10 --portfolios 32 --random-portfolios 128
PYTHONPATH=src python -m lotto_lab backtest --count 10 --steps 120
PYTHONPATH=src python -m lotto_lab verify-secondary --latest 10
```

Legacy shell entry points remain thin compatibility wrappers.

## Data refresh

The scheduled workflow runs after the Saturday draw. It:

1. scrapes the current-year primary archive;
2. determines whether draw data or generated assets need rebuilding;
3. cross-checks the newest draws against an independent source;
4. stops on disagreement;
5. rebuilds schema-v3 statistics, probability certificates, the exact 10-game reference any-prize result and SHA-256 provenance;
6. commits only verified changes directly to `main`.

It does not create recurring update branches or automated pull requests.

## Tests and release gates

CI runs Ruff, Python compilation, the unit suite, tracked-dataset/stat regeneration, JSON validation, browser JavaScript syntax checks and static-site reference tests.

v2.1.3 also has an exact confirmation workflow for probability-engine changes. It evaluates the larger 32/32/32/128 portfolio distribution so small-seed results are not promoted without confirmation.

```bash
ruff check src tests
PYTHONPATH=src python -m unittest discover -s tests -v
node --check assets/app.js
node --check assets/benchmark.js
node --check assets/certificates.js
node --check service-worker.js
```

## Responsible-use note

More games increase probability only by purchasing more unique combinations; they also increase spend. Better portfolio structure can improve lower-tier union probability for a fixed number of games, but it does not turn a random negative-expectation lottery product into an investment strategy. Set a budget you are comfortable losing.

## Documentation

- [`ROADMAP.md`](ROADMAP.md)
- [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md)
- [`docs/ODDS_OPTIMISATION.md`](docs/ODDS_OPTIMISATION.md)
- [`docs/BENCHMARKING.md`](docs/BENCHMARKING.md)
- [`docs/EXACT_ANY_PRIZE.md`](docs/EXACT_ANY_PRIZE.md)
- [`CONTRIBUTING.md`](CONTRIBUTING.md)
- [`GITHUB_PAGES.md`](GITHUB_PAGES.md)

## Current-rule references

- The Lott Help Centre: Saturday Lotto draws six winning numbers and two supplementary numbers from 45, and a prize can be won with as little as three winning numbers.
- The Lott Help Centre: one standard Saturday Lotto game has Division 1 odds of 1 in 8,145,060.

Current operator rules should always be rechecked before relying on a future release.
