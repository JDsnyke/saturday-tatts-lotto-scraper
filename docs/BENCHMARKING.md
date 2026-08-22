# Multi-seed portfolio benchmarking

This document defines the benchmark used to compare the combinatorial coverage generator with uniform random QuickPick portfolios.

## Question

For the **same number of distinct standard games**, does the coverage generator produce measurably different lower-division portfolio structure and simulated outcomes than a distribution of uniform random portfolios?

It does **not** test whether one set of numbers is more likely to be drawn. Equal-size sets of distinct standard games have the same Division 1 probability:

```text
ticket_count / C(45, 6)
```

## Why the old comparison was insufficient

A comparison between one coverage seed and one QuickPick seed can be dominated by ordinary seed-to-seed variation. A strategy should not be described as structurally better because it beat one baseline portfolio.

The multi-seed benchmark therefore compares **portfolio distributions**.

## Reference design

The generated statistics asset uses a fixed, reproducible reference benchmark:

- 10 standard games per portfolio;
- 32 independently seeded coverage portfolios;
- 128 independently seeded QuickPick portfolios;
- 2,500 shared simulated main-number draws;
- fixed root seed `20260822`;
- 120 candidate games considered per greedy coverage step;
- 1,200 bootstrap resamples for the mean-difference interval.

CLI defaults are larger and can be changed by the caller.

```bash
PYTHONPATH=src python -m lotto_lab benchmark \
  --count 10 \
  --coverage-portfolios 50 \
  --random-portfolios 200 \
  --trials 5000 \
  --seed 20260822
```

## Common random numbers

Every portfolio in a benchmark run is evaluated on the same simulated draw sample.

This is a standard variance-reduction idea: differences caused purely by one strategy seeing an easier random draw sample are removed. Portfolio-seed variation remains, which is exactly what the benchmark is intended to measure.

## Structural metrics

These are counted exactly for each generated portfolio:

- pair coverage efficiency;
- triple coverage efficiency;
- quadruple coverage efficiency;
- maximum pairwise ticket overlap;
- unique numbers represented.

Coverage efficiency is:

```text
unique covered subsets / total subset placements
```

A value of `1.0` means no repeated subset placements at that order.

## Outcome metrics

The benchmark also evaluates each portfolio on the shared simulated draws:

- **any-prize rate** — at least one ticket matches at least three main numbers;
- **Division 4 or better rate** — at least one ticket matches at least four main numbers;
- mean best main-number match per draw.

Under the current six-division Saturday Lotto structure, any ticket with at least three main numbers wins a prize, so supplementary numbers do not change the binary any-prize threshold. They still determine the exact division within some match categories.

## Distribution summaries

For coverage and QuickPick separately, each metric reports:

- mean;
- population standard deviation;
- minimum / maximum;
- 5th, 25th, 50th, 75th and 95th percentiles.

## Probability of superiority

For a metric, probability-of-superiority is the fraction of all coverage-vs-random portfolio pairs where the coverage portfolio scores better, with ties counted as one half.

Examples:

- `0.50` — no distribution-level ordering;
- `0.75` — a randomly selected coverage portfolio beats a randomly selected QuickPick portfolio about three quarters of the time on that metric;
- `1.00` — every sampled coverage portfolio beats every sampled QuickPick portfolio on that metric.

This is **not** the probability that a strategy wins the lottery.

## Bootstrap interval

The benchmark resamples the coverage and QuickPick portfolio distributions independently and calculates the favourable mean difference for every resample.

The reported 95% interval is the 2.5th–97.5th percentile range of those bootstrap differences.

Important limitation: this interval primarily describes **portfolio-seed variability conditional on the shared simulated draw sample**. A future enhancement can use nested resampling to include draw-sample uncertainty explicitly.

## Browser benchmark

`benchmark.html` provides a smaller local benchmark that runs entirely in the browser.

It is intentionally labelled exploratory:

- fewer portfolio seeds;
- fewer simulated draws;
- no backend bootstrap interval;
- useful for changing ticket counts interactively, not for release-level claims.

The precomputed repository benchmark remains the reproducible reference.

## Claim rules

A release may say the coverage algorithm improves a structural metric only when the multi-seed distribution supports that statement.

A release should not claim a lower-division outcome advantage merely because the point estimate is positive. The effect size, bootstrap interval, probability-of-superiority, sample sizes and benchmark seed must remain visible.

No result from this benchmark changes Division 1 probability for equal-size distinct portfolios.
