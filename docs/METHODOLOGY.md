# Methodology

## Claim hierarchy

Saturday Lotto Lab separates claims into five categories:

- **Exact** — combinatorial identities under the documented game rules.
- **Simulated** — Monte Carlo estimates with visible sample size and uncertainty.
- **Descriptive** — summaries of historical results.
- **Experimental** — research ideas that are plausible but not calibrated strongly enough for a probability claim.
- **Guardrail** — rules preventing descriptive patterns from being presented as prediction.

## Exact Division 1 probability

For a standard game selecting six numbers from 45:

```text
N = C(45,6) = 8,145,060
P(Division 1 | one fixed standard game) = 1/N
P(Division 1 | n distinct games in one draw) = n/N
```

The identity of those `n` combinations does not alter Division 1 probability in a fair draw.

Across `d` independent draws while owning `n` distinct games each draw:

```text
P(at least one Division 1) = 1 - (1 - n/N)^d
```

This is a probability calculation, not a recommendation to purchase additional games.

## System entries

A System `k` selection expands to every standard six-number subset of the chosen `k` numbers:

```text
standard combinations = C(k,6)
```

A System 8 therefore represents 28 standard combinations. Its Division 1 probability is the same as any other set of 28 distinct standard combinations.

## Exact prize-category probability

A fixed six-number ticket is compared with a draw containing six winning balls, two supplementary balls and 37 other balls. For exactly `m` winning and `s` supplementary matches:

```text
P(m,s) = C(6,m) × C(2,s) × C(37, 6-m-s) / C(45,6)
```

The Division 1–6 probabilities are sums of the appropriate mutually exclusive categories.

## Historical number diagnostics

Each number has marginal probability `6/45` of appearing among the six winning balls in a draw. Across `D` draws, its count has expected value:

```text
E[X] = D × 6/45
```

The per-number z-score uses the binomial marginal variance. Entropy, χ² and pair counts are retained as exploratory diagnostics. They do not feed ticket generation.

The project deliberately avoids attaching a naive χ² p-value to the 45 count cells because counts inside each draw are dependent. Formal global testing is reserved for Monte-Carlo-calibrated roadmap work.

## Combinatorial portfolio coverage

A six-number game contains:

- `C(6,2)=15` pairs;
- `C(6,3)=20` triples;
- `C(6,4)=15` quadruples.

For a set of tickets, the software counts the distinct subsets actually represented and the repeated placements. Coverage efficiency is:

```text
unique covered subsets / total subset placements
```

The v2.1 generator samples many candidate tickets for each portfolio position and uses this lexicographic objective:

1. maximise previously unseen quadruples;
2. maximise previously unseen triples;
3. maximise previously unseen pairs;
4. minimise maximum overlap with an existing game;
5. prefer lower cumulative number usage.

This objective reduces measurable redundancy. It does **not** increase any individual six-number combination's chance of being drawn.

## Monte Carlo portfolio simulation

Simulation samples eight distinct balls uniformly from 45, treats the first six as winning and the remaining two as supplementary, and evaluates the highest prize division achieved by the portfolio.

Reported hit-rate uncertainty uses a Wilson 95% interval. Simulation compares portfolio correlation/coverage; it cannot establish a predictive number-selection edge.

The reference coverage-vs-QuickPick result is reproducible but represents only one pair of seeded portfolios. The roadmap therefore keeps repeated-seed strategy-difference analysis open.

## Walk-forward historical evaluation

For each evaluated historical draw:

1. construct a new coverage and QuickPick portfolio;
2. use only the previous draw's date as a reproducible seed component;
3. do **not** feed previous winning numbers, frequencies, recency, pairs or z-scores into either generator;
4. score the generated portfolios against the later draw.

This is an out-of-sample test of portfolio structure, not a predictive backtest.

## Experimental anti-crowding research

Lottery-player selections are not uniformly distributed in many observed datasets. Published work documents preferences for birthdays/smaller numbers, 7, sequences and aesthetically meaningful patterns. In pari-mutuel prize structures, a popular combination can have more co-winners if drawn.

The anti-crowding mode therefore penalises several such features when ranking otherwise random candidate tickets. The score is **not an estimated Australian Saturday Lotto popularity probability**, and the mode must not be described as improving draw odds.

Useful background includes research on number preferences in lotteries, work on the payout cost associated with number 7, and Australian operator reporting of repeated player-picked combinations.

## Data validation and provenance

Before analysis, the loader checks:

- parseable ISO dates;
- exact column counts;
- number range 1–45;
- unique numbers within main and supplementary fields;
- no main/supplementary overlap;
- identical date sets across the two CSV files;
- no duplicate draw dates.

Generated provenance stores SHA-256 hashes for both CSVs. Scheduled updates cross-check the newest data against an independent source before publishing. A disagreement fails the update rather than silently replacing tracked data.

## Reproducibility

Seeded Python generators derive deterministic RNG seeds from SHA-256 when a string seed is supplied. Browser QuickPick uses `crypto.getRandomValues` when available. Browser-side simulations are for interactive estimates; repository reference simulations are generated by Python and checked by tests.
