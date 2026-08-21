# Saturday Lotto Lab

A probability-first Saturday Lotto / TattsLotto research project for collecting historical results, validating the dataset, exploring realised statistical variation, and generating **multi-ticket coverage sets without pretending history predicts the next draw**.

> **Key fact:** a standard Saturday Lotto entry is 6 numbers selected from 45, so there are `C(45,6) = 8,145,060` possible Division 1 combinations. Every individual combination has the same chance in a fair draw.

## What changed in v2

The old project ranked “recommended” combinations using historical main/supplementary frequency. That is not a defensible way to increase next-draw probability for an independent random lottery.

v2 replaces it with:

- **exact probability maths** rather than per-number “average odds”;
- **balanced multi-ticket coverage** that reduces internal overlap across multiple distinct entries;
- **typed Python data tooling** instead of large shell/awk pipelines;
- **strict draw validation** and canonical CSV ordering;
- **historical diagnostics** (z-scores, entropy, χ² distance, pair co-occurrence) clearly labelled descriptive;
- **a redesigned GitHub Pages dashboard** with responsive UI, light/dark/system themes, animated charts, accessible tabs and an in-browser Ticket Lab;
- **unit tests + Ruff linting** in CI;
- **quiet automation**: no automated dependency PR churn and no updater-created branches/PRs.

## Quick start

Requires Python 3.11+.

```bash
git clone https://github.com/JDsnyke/saturday-tatts-lotto-scraper.git
cd saturday-tatts-lotto-scraper
python3 -m pip install -r requirements.txt
export PYTHONPATH="$PWD/src"
```

Validate and canonicalize the existing dataset:

```bash
python3 -m lotto_lab validate
```

Refresh the current year's results and rebuild website statistics:

```bash
python3 -m lotto_lab refresh
```

Generate 10 balanced-coverage entries:

```bash
python3 -m lotto_lab tickets --count 10 --mode coverage
```

Generate reproducible entries for testing/research:

```bash
python3 -m lotto_lab tickets --count 10 --mode coverage --seed demo-2026
```

The legacy shell entry points remain as thin wrappers (`master_lotto.sh`, `scrape_lotto_results.sh`, `generate_stats.sh`, `parse_and_recommend.sh`, `clean_csv.sh`) so existing usage does not abruptly break.

## Ticket modes

### Balanced coverage

Coverage mode greedily spreads number usage and avoids repeatedly using the same number pairs across the ticket set. It is designed for **portfolio diversity** when generating multiple distinct entries.

It does **not** make a chosen number more likely to be drawn and does not change the per-combination probability.

### Uniform QuickPick

Random mode samples distinct six-number combinations uniformly. With no seed it uses the operating system's cryptographic random source through Python's `SystemRandom`.

## Probability

For one standard ticket:

```text
P(Division 1) = 1 / C(45,6)
              = 1 / 8,145,060
```

For `n` distinct standard tickets:

```text
P(Division 1) = n / 8,145,060
```

Because a draw produces one winning six-number set, these mutually exclusive covered combinations make the multi-ticket Division 1 probability linear in the number of **distinct** entries.

## Historical diagnostics

The website and `assets/lotto_stats.json` expose:

- observed main and supplementary counts for each number;
- marginal binomial z-scores for main-number counts;
- normalized entropy of the main-number distribution;
- a χ² distance from equal historical counts (descriptive only, no naive p-value);
- draws since last main appearance;
- common historical pairs and lift versus expected pair co-occurrence;
- a reproducible reference coverage set.

See [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) for the reasoning and formulas.

## Data pipeline

The scraper still uses the public `au.lottonumbers.com` archive as its collection source, but the implementation is now Python + Beautiful Soup with:

- a dynamic current year instead of a hard-coded 2025 ceiling;
- a user agent, timeout and polite request delay;
- link deduplication;
- validation before data is accepted;
- canonical newest-first output;
- current-year incremental refresh by default.

The scheduled GitHub Action runs once per week after the Saturday draw, rebuilds statistics, and commits directly to `main` **only when tracked draw data changed**. It does not create update branches or pull requests.

## Development

```bash
python3 -m pip install -r requirements-dev.txt
PYTHONPATH=src python3 -m unittest discover -s tests -v
ruff check src tests
```

CI also compiles all Python modules, validates the tracked historical dataset, and checks that the static web assets referenced by `index.html` exist.

## Repository layout

```text
src/lotto_lab/
  analysis.py       # descriptive statistics + website JSON
  cli.py            # command-line interface
  data.py           # CSV parsing/validation/canonical writing
  domain.py         # game constants and Draw model
  probability.py    # exact combinatorics + diagnostics
  scrape.py         # public results scraper
  tickets.py        # random and balanced coverage generators
assets/
  app.css
  app.js
  lotto_stats.json
.github/workflows/
  ci.yml
  data-refresh.yml
  deploy.yml
tests/
docs/METHODOLOGY.md
ROADMAP.md
```

## Roadmap

The living implementation plan is in [`ROADMAP.md`](ROADMAP.md). Future work prioritises provenance, second-source verification, walk-forward/Monte Carlo comparison, and stronger randomness diagnostics—not “AI prediction”.

## Responsible use

This project is for educational and research purposes. Lottery games are games of chance and involve financial risk. Historical patterns do not guarantee or meaningfully predict future winning numbers in a fair draw. Set a budget and gamble responsibly.

## License

MIT. See [`LICENSE`](LICENSE).
