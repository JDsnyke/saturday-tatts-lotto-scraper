# Multi-seed and certified portfolio benchmarking

This document defines the evidence framework used to compare Saturday Lotto portfolio generators.

The project separates three kinds of evidence:

1. **exact combinatorics and certificates**;
2. **structural portfolio metrics**;
3. **out-of-sample Monte Carlo comparisons**.

None of these changes the probability of an individual six-number combination being drawn.

## Division 1 invariant

For the same number of distinct standard games, every portfolio has identical Division 1 probability:

```text
ticket_count / C(45, 6)
```

The benchmark therefore studies only lower-division portfolio overlap and coverage.

## Exact event-intersection mathematics

For two six-number tickets sharing `r` numbers, the 45 balls can be partitioned into:

- `r` shared numbers;
- `6-r` numbers unique to ticket A;
- `6-r` numbers unique to ticket B;
- `33+r` numbers in neither ticket.

For a threshold `k`, the code sums all six-main-number draws in which both tickets match at least `k` numbers. This gives the **exact pair-event intersection probability**.

For the any-prize event, `k=3` because every current Saturday Lotto prize division requires at least three winning main numbers. For Division 4 or better, `k=4`.

Known exact intersection counts for selected cases include:

```text
>=3 main, overlap 0: 400 winning-main sets
>=3 main, overlap 1: 3,700 winning-main sets
>=4 main, overlap 0: 0
>=4 main, overlap 1: 0
>=4 main, overlap 2: 36
```

Each count is divided by `C(45,6)` to obtain its probability.

## Bonferroni portfolio lower bound

For portfolio events `A1 ... An`, the code computes:

```text
S1 = sum P(Ai)
S2 = sum P(Ai ∩ Aj), i < j

P(A1 ∪ ... ∪ An) >= max(0, S1 - S2)
```

This is a rigorous second-order Bonferroni lower bound.

For the any-prize objective, this bound is useful because exact pairwise overlap is a major source of portfolio redundancy. It is still a **lower bound**, not the exact union probability unless additional intersection structure is proved absent.

## Exact Division-4-or-better certificate

If every pair of portfolio tickets shares at most one number, their `>=4 main` events are pairwise disjoint.

Reason: two six-number tickets with overlap at most one would require at least

```text
4 + 4 - 1 = 7
```

distinct winning main numbers for both to match four or more. Saturday Lotto draws only six winning main numbers.

Therefore, for such a portfolio:

```text
P(at least one ticket matches >=4 main)
  = ticket_count * P(one ticket matches >=4 main)
```

The right-hand side is also the universal union upper bound. The portfolio is therefore **globally optimal for Division 4-or-better probability at that ticket count**.

This is an exact theorem, not a simulation result.

## Ticket objectives

The CLI exposes separate generation modes because they optimise different things:

- `coverage` — generic quadruple → triple → pair subset diversity;
- `any-prize-bound` — minimises exact pairwise `>=3 main` event-intersection cost, thereby maximising the second-order any-prize lower bound greedily;
- `division4-bound` — minimises exact `>=4 main` pair-event intersection cost, then uses the any-prize pair cost and structural coverage as tie-breakers;
- `random` — uniform QuickPick baseline;
- `anti-crowding` — experimental conditional prize-sharing research only.

Example:

```bash
PYTHONPATH=src python -m lotto_lab tickets --count 10 --mode any-prize-bound --json
PYTHONPATH=src python -m lotto_lab tickets --count 10 --mode division4-bound --json
```

The JSON metrics include both any-prize and Division-4-or-better probability certificates.

## Why sampled-training optimisation was rejected

A prototype directly selected tickets by maximising any-prize hits on a simulated training draw sample.

Held-out experiments showed a large training/validation gap and no improvement over the existing coverage design. The reason is intuitive: marginal differences between strong portfolios are small compared with sampling noise, so a finite training sample can reward lucky candidate tickets rather than genuinely better structure.

That optimiser is **not shipped as a recommended strategy**.

Any future stochastic optimiser must:

- use separate training and validation draw samples;
- report the training/validation gap;
- beat the existing structural baseline out of sample;
- avoid describing training performance as evidence.

## Multi-seed coverage benchmark

The generated statistics asset keeps the fixed v2.1.1 reference benchmark for reproducibility:

- 10 standard games per portfolio;
- 32 independently seeded coverage portfolios;
- 128 independently seeded QuickPick portfolios;
- 2,500 shared simulated main-number draws;
- root seed `20260822`;
- 120 candidate games per coverage step;
- 1,200 bootstrap resamples.

```bash
PYTHONPATH=src python -m lotto_lab benchmark \
  --count 10 \
  --coverage-portfolios 50 \
  --random-portfolios 200 \
  --trials 5000 \
  --seed 20260822
```

The fixed reference design is intentionally not silently changed when new objective modes are added. That preserves release-to-release comparability.

## Certified-objective benchmark

The additional objective benchmark compares:

- generic subset coverage;
- any-prize-bound portfolios;
- Division-4-bound portfolios;
- QuickPick portfolios.

All strategies are evaluated on the same simulated draw sample. The bound-driven generators themselves do **not** train on those simulated outcomes; their objectives come from exact pair-event combinatorics.

```bash
PYTHONPATH=src python -m lotto_lab benchmark-objectives \
  --count 10 \
  --portfolios 24 \
  --random-portfolios 96 \
  --trials 5000 \
  --seed 20260822 \
  --candidates-per-ticket 320
```

Reported metrics include:

- any-prize Bonferroni lower bound;
- simulated any-prize rate;
- certified Division-4-or-better probability;
- simulated Division-4-or-better rate;
- proportion of portfolios receiving the exact global-optimality certificate;
- triple coverage efficiency;
- maximum pairwise overlap.

The objective benchmark is designed to answer a stricter question: **does a mathematically targeted objective actually improve on the existing coverage generator, or does the existing generator already reach the same useful structure?**

## Common random numbers

Every portfolio in one benchmark run is evaluated on the same simulated draw sample.

This reduces irrelevant Monte Carlo noise caused by different strategies seeing different random outcomes. Portfolio-seed variation remains, which is the intended comparison dimension.

## Distribution summaries

Each benchmark metric can report:

- mean;
- population standard deviation;
- minimum / maximum;
- 5th, 25th, 50th, 75th and 95th percentiles.

## Probability of superiority

Probability-of-superiority is the fraction of all strategy-vs-baseline portfolio pairs where the named strategy scores better on the named metric, with ties counted as one half.

This is **not** the probability that a strategy wins the lottery.

## Bootstrap interval

The benchmark independently resamples the compared portfolio distributions and calculates the favourable mean difference.

The 95% interval is the 2.5th–97.5th percentile range of those bootstrap differences.

Current limitation: this interval primarily describes **portfolio-seed variability conditional on the shared simulated draw sample**. Nested draw+portfolio resampling remains roadmap work.

## Browser benchmark and certificates

`benchmark.html` provides two evidence layers:

- the existing smaller local exploratory multi-seed benchmark;
- a Certified Probability panel populated from the generated reference coverage-set metrics.

The certificate panel labels exact bounds separately from simulated estimates. If the current static statistics asset predates v2.1.2, the panel explicitly reports that a refreshed asset is pending rather than inventing values.

## Claim rules

- Never say a bound is exact unless the conditions for exactness have been proved.
- Never infer a Division 1 advantage from lower-order portfolio structure.
- Never report simulated training performance as evidence for a generator.
- Never call probability-of-superiority the probability of winning.
- Prefer exact certificates over Monte Carlo when the exact theorem applies.
- If a targeted objective does not outperform the existing coverage generator out of sample, keep the simpler existing generator as the default.
