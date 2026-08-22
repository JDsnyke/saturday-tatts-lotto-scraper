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

Under the current Saturday Lotto prize structure, **winning any prize is equivalent to matching at least three winning main numbers**. Supplementary matches decide which division applies within some categories, but do not change the binary any-prize event.

Likewise, **Division 4 or better is equivalent to matching at least four winning main numbers**.

## Exact two-ticket event intersections

For two six-number tickets sharing `r` numbers, partition the 45 balls into:

- `r` shared numbers;
- `6-r` numbers found only in ticket A;
- `6-r` numbers found only in ticket B;
- `33+r` numbers in neither ticket.

For a threshold `k`, sum all ways to choose six winning main numbers such that both tickets receive at least `k` matches.

If `x` shared, `y` A-only, `z` B-only and `w` neither numbers are selected, each valid term contributes:

```text
C(r,x) × C(6-r,y) × C(6-r,z) × C(33+r,w)
```

subject to:

```text
x + y >= k
x + z >= k
x + y + z + w = 6
```

The exact pair-event probability is the resulting count divided by `C(45,6)`.

This calculation is used by the certified portfolio objectives and does not depend on historical draw data or Monte Carlo sampling.

## Bonferroni portfolio lower bound

Let `Ai` be the event that portfolio ticket `i` reaches a chosen main-match threshold. Define:

```text
S1 = Σ P(Ai)
S2 = Σ P(Ai ∩ Aj), i < j
```

The second-order Bonferroni inequality gives:

```text
P(A1 ∪ ... ∪ An) >= max(0, S1 - S2)
```

The software computes both terms exactly.

For the any-prize event (`k=3`), this is a **rigorous lower bound**, not generally the exact portfolio probability because three-way and higher intersections can remain.

The ordinary union bound gives:

```text
P(A1 ∪ ... ∪ An) <= min(1, S1)
```

When pairwise intersections are zero, the lower and upper bounds meet and the exact probability is known.

## Exact Division-4-or-better optimality theorem

Take two six-number games with at most one shared number. If both were to match at least four of the same six winning main numbers, at least:

```text
4 + 4 - 1 = 7
```

distinct winning numbers would be required. Only six winning main numbers exist.

Therefore their `>=4 main` events cannot occur together.

If **every pair** in a portfolio shares at most one number, all pairwise `>=4 main` intersections are zero. The portfolio probability is then exactly:

```text
P(at least one game reaches >=4 main)
  = n × P(one game reaches >=4 main)
```

No union of `n` events with those same marginal probabilities can exceed their sum. Such a portfolio therefore reaches the **global maximum possible Division-4-or-better probability for that ticket count**.

This is an exact certificate and takes precedence over Monte Carlo evidence when it applies.

## Combinatorial portfolio coverage

A six-number game contains:

- `C(6,2)=15` pairs;
- `C(6,3)=20` triples;
- `C(6,4)=15` quadruples.

For a set of tickets, the software counts the distinct subsets actually represented and the repeated placements. Coverage efficiency is:

```text
unique covered subsets / total subset placements
```

The generic coverage generator samples candidate tickets and uses this lexicographic objective:

1. maximise previously unseen quadruples;
2. maximise previously unseen triples;
3. maximise previously unseen pairs;
4. minimise maximum overlap with an existing game;
5. prefer lower cumulative number usage.

This objective reduces measurable redundancy. It does **not** increase any individual six-number combination's chance of being drawn.

## Certified bound-driven objectives

Two additional generators optimise exact pair-event mathematics rather than historical or simulated outcomes.

### Any-prize bound

Every candidate six-number game has the same single-ticket any-prize probability. Therefore, within a greedy step, increasing the second-order Bonferroni lower bound is equivalent to reducing the sum of exact pairwise `>=3 main` event intersections with already selected games.

The generator uses that pair-event cost as its primary objective and structural coverage only as a tie-breaker.

It optimises a **rigorous lower bound**, not the exact any-prize union.

### Division-4 bound

The Division-4-bound generator first minimises exact pairwise `>=4 main` intersections, then uses the any-prize pair cost and subset coverage as tie-breakers.

If the resulting portfolio receives the pairwise-disjoint certificate, its Division-4-or-better probability is exact and globally optimal for the ticket count.

If not, the software reports only the available lower bound and does not label the result globally optimal.

## Why direct simulated-training optimisation is not shipped

A prototype attempted to optimise any-prize union directly by selecting candidate games that covered the most simulated training draws.

Held-out experiments showed a substantial training/validation gap. The optimiser learned sampling noise and did not improve on the existing coverage design when evaluated on independent draws.

That prototype is deliberately excluded from the recommended generators.

Future stochastic optimisation work must use separate training and validation samples, report the generalisation gap and outperform the structural baseline out of sample before being considered for release.

## Monte Carlo portfolio simulation

Simulation samples eight distinct balls uniformly from 45, treats the first six as winning and the remaining two as supplementary, and evaluates the highest prize division achieved by the portfolio.

Reported hit-rate uncertainty uses a Wilson 95% interval. Simulation compares portfolio correlation/coverage; it cannot establish a predictive number-selection edge.

## Multi-seed benchmark

The repository benchmark compares **distributions** of independently seeded coverage and QuickPick portfolios on one shared simulated draw sample.

It reports:

- structural metric distributions;
- lower-division outcome distributions;
- random-baseline quantiles;
- probability-of-superiority;
- bootstrap intervals for favourable mean differences.

The shared-draw design reduces irrelevant Monte Carlo noise between strategies. Current bootstrap intervals primarily represent portfolio-seed uncertainty conditional on that draw sample. Nested draw+portfolio uncertainty remains roadmap work.

See [`BENCHMARKING.md`](BENCHMARKING.md) for the fixed reference design and the certified-objective benchmark.

## Walk-forward historical evaluation

For each evaluated historical draw:

1. construct a new coverage and QuickPick portfolio;
2. use only the previous draw's date as a reproducible seed component;
3. do **not** feed previous winning numbers, frequencies, recency, pairs or z-scores into either generator;
4. score the generated portfolios against the later draw.

This is an out-of-sample test of portfolio structure, not a predictive backtest.

## Historical number diagnostics

Each number has marginal probability `6/45` of appearing among the six winning balls in a draw. Across `D` draws, its count has expected value:

```text
E[X] = D × 6/45
```

The per-number z-score uses the binomial marginal variance. Entropy, χ² and pair counts are retained as exploratory diagnostics. They do not feed ticket generation.

The project deliberately avoids attaching a naive χ² p-value to the 45 count cells because counts inside each draw are dependent. Formal global testing is reserved for Monte-Carlo-calibrated roadmap work.

## Experimental anti-crowding research

Lottery-player selections are not uniformly distributed in many observed datasets. Published work documents preferences for birthdays/smaller numbers, 7, sequences and aesthetically meaningful patterns. In pari-mutuel prize structures, a popular combination can have more co-winners if drawn.

The anti-crowding mode therefore penalises several such features when ranking otherwise random candidate tickets. The score is **not an estimated Australian Saturday Lotto popularity probability**, and the mode must not be described as improving draw odds.

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
