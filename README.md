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
2. **Reduce portfolio redundancy** — for a fixed number of games, maximise unique pairs, triples and quadruples so multiple tickets overlap less at lower orders.
3. **Conditional prize-sharing research** — experimentally avoid patterns people may choose disproportionately. This does not improve the chance of being drawn; it may matter only to how many people share a pari-mutuel prize if that combination wins.

See [`docs/ODDS_OPTIMISATION.md`](docs/ODDS_OPTIMISATION.md) for the claim hierarchy and limitations.

## v2.1 highlights

### Exact probability engine

- exact Division 1 combination count and multi-game probability;
- cumulative probability across repeated independent draws;
- System 6–20 equivalence via `C(k, 6)` standard combinations;
- exact 0–6 main-number match distribution;
- exact Division 1–6 standard-game probabilities under the current 6 winning + 2 supplementary rules;
- exact overall standard-game any-prize probability.

### Combinatorial portfolio optimiser

`coverage` mode searches candidate games and prioritises:

1. new four-number subsets;
2. new three-number subsets;
3. new pairs;
4. lower maximum game-to-game overlap;
5. balanced number usage.

The result is measurable with pair/triple/quadruple coverage efficiency. It is a portfolio-structure optimisation, not a prediction model.

### Multi-seed benchmark

v2.1.1 replaces the weak “one coverage seed vs one QuickPick seed” inference with a distribution benchmark:

- independently seeded coverage portfolios;
- a larger distribution of independently seeded QuickPick portfolios;
- the same simulated draw sample applied to every portfolio;
- 5th/25th/50th/75th/95th percentile summaries;
- probability-of-superiority;
- bootstrap 95% intervals for the favourable mean strategy difference;
- fixed reference seeds and sample sizes documented in [`docs/BENCHMARKING.md`](docs/BENCHMARKING.md).

Equal-size sets of distinct games still have **identical Division 1 probability**. The benchmark measures lower-division portfolio diversification.

A dedicated static [`benchmark.html`](benchmark.html) page can also run a smaller exploratory benchmark locally in the browser.

### Evidence layer

- Monte Carlo portfolio evaluation with actual Saturday Lotto prize divisions;
- Wilson 95% confidence intervals;
- leakage-free walk-forward comparison against historical draws;
- multi-seed distribution benchmarking rather than a single baseline seed;
- explicit effect-size and uncertainty labels.

### Experimental anti-crowding mode

The optional anti-crowding generator penalises birthday-heavy games, number 7, consecutive pairs and very evenly spaced selections. It is based on published evidence that lottery players make non-uniform choices, but it is **not calibrated to Australian Saturday Lotto player-level ticket data**.

It must never be interpreted as increasing draw probability.

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
- upgraded Ticket Lab with coverage, QuickPick and experimental anti-crowding modes;
- pair/triple/quadruple coverage metrics;
- local portfolio any-prize simulation with confidence interval;
- shareable ticket-set URLs and CSV export;
- Strategy Evidence view;
- Draw Explorer with date/search/number filters and CSV export;
- accessible keyboard frequency chart;
- data freshness and provenance display;
- dedicated Benchmark Lab with client-side multi-seed runs and JSON export;
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
PYTHONPATH=src python -m lotto_lab tickets --count 10 --mode random
PYTHONPATH=src python -m lotto_lab tickets --count 10 --mode anti-crowding
PYTHONPATH=src python -m lotto_lab simulate --count 10 --trials 50000
PYTHONPATH=src python -m lotto_lab benchmark --count 10 --coverage-portfolios 50 --random-portfolios 200 --trials 5000
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
5. rebuilds schema-v3 statistics, reference evidence and SHA-256 provenance;
6. commits only verified changes directly to `main`.

It does not create recurring update branches or automated pull requests.

## Tests

CI runs Ruff, Python compilation, the unit suite, tracked-dataset validation/stat regeneration, JSON validation, browser JavaScript syntax checks and static-site reference tests.

```bash
ruff check src tests
PYTHONPATH=src python -m unittest discover -s tests -v
node --check assets/app.js
node --check assets/benchmark.js
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
