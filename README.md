# Saturday Lotto Probability Lab

An open-source Saturday Lotto / TattsLotto research project focused on **exact probability, data quality, multi-entry portfolio structure and honest uncertainty**.

The project deliberately does **not** claim that hot, cold, overdue, recently drawn or historically common numbers are more likely in the next fair draw.

## What can actually improve?

For the current 6-from-45 game there are exactly:

```text
C(45, 6) = 8,145,060
```

possible standard six-number combinations. Therefore one standard game has Division 1 probability `1 / 8,145,060`, while `n` distinct standard games have probability `n / 8,145,060` in one draw.

Number selection cannot improve that probability if the draw is fair. Objective optimisation instead falls into three separate categories:

1. **Own more distinct combinations** — the only direct Division 1 probability increase.
2. **Reduce portfolio redundancy** — structure multiple games so their lower-tier winning events overlap less.
3. **Conditional prize-sharing research** — experimentally avoid patterns people may choose disproportionately. This does not improve the chance of being drawn; it may matter only to how many people share a pari-mutuel prize if that combination wins.

See [`docs/ODDS_OPTIMISATION.md`](docs/ODDS_OPTIMISATION.md) and [`docs/BENCHMARKING.md`](docs/BENCHMARKING.md) for the claim hierarchy and limitations.

## v2.1.2 highlights

### Exact portfolio probability certificates

v2.1.2 adds exact two-ticket event-intersection combinatorics and portfolio certificates.

For a portfolio event such as “at least one game matches three or more main numbers”, the code computes the exact first- and second-order terms:

```text
S1 = sum P(Ai)
S2 = sum P(Ai ∩ Aj)

P(any event) >= max(0, S1 - S2)
```

This is a rigorous Bonferroni lower bound, not a simulation estimate.

For **Division 4 or better**, there is a stronger exact result. If every pair of six-number games shares at most one number, two games cannot both match four or more of the same six winning main numbers. Their `>=4 main` events are pairwise disjoint, so:

```text
P(Division 4 or better somewhere in portfolio)
  = ticket_count × P(one game matches >=4 main)
```

That reaches the universal sum-of-marginals upper bound, so the portfolio is **globally optimal for Division 4-or-better probability at that ticket count**.

### Separate ticket objectives

The CLI now keeps distinct objectives separate instead of pretending one heuristic is universally best:

- `coverage` — generic quadruple → triple → pair subset diversity;
- `any-prize-bound` — greedily minimises exact pairwise `>=3 main` event-intersection cost, improving the rigorous second-order any-prize lower bound;
- `division4-bound` — minimises exact pairwise `>=4 main` event intersections and can return a global-optimality certificate;
- `random` — uniform QuickPick baseline;
- `anti-crowding` — experimental conditional prize-sharing research only.

Every generated portfolio reports probability certificates in `ticket_metrics`.

### A rejected optimiser is also a result

A direct prototype trained ticket selection on simulated any-prize outcomes. It performed very strongly on its training draws but failed to improve on the existing coverage design on held-out draws.

That sampled-training optimiser is **not shipped as a recommended strategy**. The project records this negative result explicitly so future work does not reintroduce training-sample overfitting as an apparent lottery edge.

### Multi-seed benchmark

v2.1.1 replaced the weak “one coverage seed vs one QuickPick seed” inference with a distribution benchmark:

- independently seeded coverage portfolios;
- a larger distribution of independently seeded QuickPick portfolios;
- the same simulated draw sample applied to every portfolio;
- 5th/25th/50th/75th/95th percentile summaries;
- probability-of-superiority;
- bootstrap 95% intervals for favourable mean strategy differences;
- fixed reference seeds and sample sizes documented in [`docs/BENCHMARKING.md`](docs/BENCHMARKING.md).

v2.1.2 adds a separate `benchmark-objectives` command to compare generic coverage, any-prize-bound, Division-4-bound and QuickPick portfolios on held-out shared draws.

Equal-size sets of distinct games always have **identical Division 1 probability**.

### Exact probability engine

- exact Division 1 combination count and multi-game probability;
- cumulative probability across repeated independent draws;
- System 6–20 equivalence via `C(k, 6)` standard combinations;
- exact 0–6 main-number match distribution;
- exact Division 1–6 standard-game probabilities;
- exact overall standard-game any-prize probability;
- exact two-ticket `>=k main` event-intersection probabilities;
- rigorous portfolio union lower bounds and exact disjoint-event certificates.

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
- local portfolio any-prize simulation with confidence interval;
- shareable ticket-set URLs and CSV export;
- Strategy Evidence view;
- Draw Explorer with date/search/number filters and CSV export;
- accessible keyboard frequency chart;
- data freshness and provenance display;
- dedicated Benchmark Lab with client-side multi-seed runs and JSON export;
- **Certified Probability** panel separating exact bounds from simulated evidence;
- system/light/dark themes;
- offline/PWA cache support.

No framework or external browser runtime is required: the published dashboard stays a static GitHub Pages application.

## CLI

Install dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Run with the source tree:

```bash
PYTHONPATH=src python -m lotto_lab validate
PYTHONPATH=src python -m lotto_lab stats
PYTHONPATH=src python -m lotto_lab tickets --count 10 --mode coverage
PYTHONPATH=src python -m lotto_lab tickets --count 10 --mode any-prize-bound --json
PYTHONPATH=src python -m lotto_lab tickets --count 10 --mode division4-bound --json
PYTHONPATH=src python -m lotto_lab tickets --count 10 --mode random
PYTHONPATH=src python -m lotto_lab tickets --count 10 --mode anti-crowding
PYTHONPATH=src python -m lotto_lab simulate --count 10 --trials 50000
PYTHONPATH=src python -m lotto_lab benchmark --count 10 --coverage-portfolios 50 --random-portfolios 200 --trials 5000
PYTHONPATH=src python -m lotto_lab benchmark-objectives --count 10 --portfolios 24 --random-portfolios 96 --trials 5000
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
5. rebuilds schema-v3 statistics, reference evidence, probability certificates and SHA-256 provenance;
6. commits only verified changes directly to `main`.

It does not create recurring update branches or automated pull requests.

## Tests

CI runs Ruff, Python compilation, the unit suite, tracked-dataset validation/stat regeneration, JSON validation, browser JavaScript syntax checks and static-site reference tests.

```bash
ruff check src tests
PYTHONPATH=src python -m unittest discover -s tests -v
node --check assets/app.js
node --check assets/benchmark.js
node --check assets/certificates.js
node --check service-worker.js
```

## Responsible-use note

More games increase probability only by purchasing more unique combinations; they also increase spend. Historical analysis does not turn a random negative-expectation lottery product into an investment strategy. Set a budget you are comfortable losing.

## Documentation

- [`ROADMAP.md`](ROADMAP.md)
- [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md)
- [`docs/ODDS_OPTIMISATION.md`](docs/ODDS_OPTIMISATION.md)
- [`docs/BENCHMARKING.md`](docs/BENCHMARKING.md)
- [`CONTRIBUTING.md`](CONTRIBUTING.md)
- [`GITHUB_PAGES.md`](GITHUB_PAGES.md)

## References

Current game rules and odds should be checked against the official operator before relying on a release. Research references for human number-choice behaviour are linked from the methodology and dashboard.
