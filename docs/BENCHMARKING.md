# Multi-seed, certified and exact portfolio benchmarking

This document defines the evidence framework used to compare Saturday Lotto portfolio generators.

The project separates four kinds of evidence:

1. **exact finite-portfolio probability**;
2. **exact combinatorial bounds and certificates**;
3. **structural portfolio metrics**;
4. **out-of-sample Monte Carlo comparisons** for questions not solved exactly.

None changes the probability of an individual six-number combination being drawn.

## Division 1 invariant

For the same number of distinct standard games, every portfolio has identical Division 1 probability:

```text
ticket_count / C(45, 6)
```

The benchmark therefore studies only lower-division portfolio overlap and coverage.

## Exact fixed-portfolio any-prize probability

v2.1.3 can compute the exact probability that at least one game in a practical smaller portfolio matches three or more of the six winning main numbers.

The algorithm counts the complement with finite-state dynamic programming. Each ticket keeps a base-3 match counter with surviving states 0, 1 and 2; any transition that would create a third match is excluded. The remaining six-ball selections are exactly the winning-main sets in which no ticket wins a prize.

```text
exact any-prize probability
  = 1 - no-prize winning-main sets / C(45,6)
```

There is no random draw sample in this calculation. See [`EXACT_ANY_PRIZE.md`](EXACT_ANY_PRIZE.md).

## Exact event-intersection mathematics

For two six-number tickets sharing `r` numbers, the 45 balls can be partitioned into:

- `r` shared numbers;
- `6-r` numbers unique to ticket A;
- `6-r` numbers unique to ticket B;
- `33+r` numbers in neither ticket.

For a threshold `k`, the code sums all six-main-number draws in which both tickets match at least `k` numbers. This gives the **exact pair-event intersection probability**.

For the any-prize event, `k=3` because a current Saturday Lotto prize can be won with three winning main numbers. For Division 4 or better, `k=4`.

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

For the any-prize objective, it remains useful as a cheap construction score even though v2.1.3 can exactly evaluate smaller completed portfolios. It is not labelled as the exact union unless the required intersection conditions prove exactness.

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

- `coverage` — generic quadruple → triple → pair subset diversity; recommended balanced default;
- `any-prize-bound` — minimises exact pairwise `>=3 main` event-intersection cost, thereby maximising the second-order any-prize lower bound greedily;
- `division4-bound` — minimises exact `>=4 main` pair-event intersection cost, then uses the any-prize pair cost and structural coverage as tie-breakers;
- `random` — uniform QuickPick baseline;
- `anti-crowding` — experimental conditional prize-sharing research only and excluded from draw-probability objective comparisons.

Examples:

```bash
PYTHONPATH=src python -m lotto_lab tickets --count 10 --mode coverage
PYTHONPATH=src python -m lotto_lab tickets --count 10 --mode any-prize-bound --json
PYTHONPATH=src python -m lotto_lab exact-any-prize --count 10 --mode coverage
```

## Why sampled-training optimisation was rejected

A prototype directly selected tickets by maximising any-prize hits on a simulated training draw sample.

Held-out experiments showed a large training/validation gap and no improvement over the existing Coverage design. Marginal differences among strong portfolios are small compared with finite-sample draw noise, so a training sample can reward lucky candidate tickets rather than genuinely better structure.

That optimiser is **not shipped as a recommended strategy**.

Future stronger search should use exact evaluation where practical, or strict training/validation separation where an exact objective is too expensive to use inside every search step.

## v2.1.1 simulated Coverage benchmark

The generated statistics asset keeps the fixed v2.1.1 reference benchmark for reproducibility:

- 10 standard games per portfolio;
- 32 independently seeded Coverage portfolios;
- 128 independently seeded QuickPick portfolios;
- 2,500 shared simulated main-number draws;
- root seed `20260822`;
- 120 candidate games per Coverage step;
- 1,200 bootstrap resamples.

```bash
PYTHONPATH=src python -m lotto_lab benchmark \
  --count 10 \
  --coverage-portfolios 50 \
  --random-portfolios 200 \
  --trials 5000 \
  --seed 20260822
```

The old reference is intentionally retained rather than rewritten after later results are known.

## v2.1.2 certified-objective benchmark

The v2.1.2 objective benchmark compares:

- generic subset Coverage;
- Any-prize-bound portfolios;
- Division-4-bound portfolios;
- QuickPick portfolios.

All strategies are evaluated on the same simulated draw sample. The bound-driven generators themselves do **not** train on those outcomes; their objectives come from exact pair-event combinatorics.

```bash
PYTHONPATH=src python -m lotto_lab benchmark-objectives \
  --count 10 \
  --portfolios 24 \
  --random-portfolios 96 \
  --trials 5000 \
  --seed 20260822 \
  --candidates-per-ticket 320
```

The benchmark also suppresses Monte Carlo inference when an exact certificate proves that the compared true probabilities are equal. A finite simulation is not allowed to overrule an exact theorem.

## v2.1.3 exact any-prize objective benchmark

`benchmark-exact-objectives` evaluates the same portfolio-generator families using the **exact any-prize probability of every completed portfolio**.

The deterministic seed names intentionally match the v2.1.2 objective benchmark:

```text
objective:{root_seed}:{strategy}:{index}
```

This allows exact evaluation to resolve earlier Monte Carlo ambiguity without changing the portfolio experiment after observing results.

Example:

```bash
PYTHONPATH=src python -m lotto_lab benchmark-exact-objectives \
  --count 10 \
  --portfolios 32 \
  --random-portfolios 128 \
  --seed 20260822 \
  --candidates-per-ticket 320 \
  --bootstrap-resamples 2000
```

### Initial 12-seed exact run

The first exact release-gate run used 12 portfolios per structured objective and 48 QuickPick portfolios. It favoured Any-prize-bound over Coverage by about **+0.00714 percentage points**, with a narrowly positive portfolio-seed bootstrap interval.

That result was treated as provisional because the effect was extremely small and the structured sample contained only 12 seeds.

### Larger confirmation run

Before changing the product recommendation, the project expanded the exact benchmark to:

- 10 games per portfolio;
- 32 Coverage portfolios;
- 32 Any-prize-bound portfolios;
- 32 Division-4-bound portfolios;
- 128 QuickPick portfolios;
- root seed `20260822`;
- 320 candidates per greedy construction step;
- 2,000 bootstrap resamples across portfolio seeds.

Mean exact any-prize probabilities:

| Strategy | Exact mean any-prize probability |
| --- | ---: |
| Coverage | **23.00372595%** |
| Any-prize-bound | 23.00482171% |
| Division-4-bound | 23.00703433% |
| QuickPick | **21.44444742%** |

#### Coverage vs QuickPick

- exact mean difference: **+1.55927853 percentage points**;
- portfolio-seed bootstrap 95% interval: **+1.47685128 to +1.65048178 points**;
- probability-of-superiority: **1.000** in this fixed benchmark.

Every one of the 32 tested Coverage portfolios had a higher exact any-prize probability than every one of the 128 tested QuickPick portfolios.

This is a strong result for lower-tier portfolio diversification, **not** a future-number prediction and **not** a Division 1 advantage.

#### Any-prize-bound vs Coverage

- exact mean difference: **+0.00109576 percentage points**;
- portfolio-seed bootstrap 95% interval: **−0.00506409 to +0.00720569 points**;
- probability-of-superiority: **0.4834**.

The larger exact distribution does not demonstrate a reliable advantage over Coverage.

#### Division-4-bound vs Coverage on any-prize probability

- exact mean difference: **+0.00330837 percentage points**;
- portfolio-seed bootstrap 95% interval: **−0.00168163 to +0.00869012 points**;
- probability-of-superiority: **0.4443**.

Again, the interval crosses zero. Division-4-bound remains valuable for its separate exact Division-4+ objective, not because this run proves higher any-prize probability.

### Release conclusion

**Coverage remains the recommended balanced default.**

The project explicitly retains the smaller 12-seed result that favoured Any-prize-bound, while using the larger confirmation distribution to set the release recommendation. This is intended to reduce result-selection bias.

## Common random numbers

For benchmarks that still use Monte Carlo, every portfolio in one run is evaluated on the same simulated draw sample.

This reduces irrelevant noise caused by different strategies seeing different random outcomes. It is not needed for the v2.1.3 exact any-prize benchmark because there is no simulated draw sample.

## Distribution summaries

Each benchmark metric can report:

- mean;
- population standard deviation;
- minimum / maximum;
- 5th, 25th, 50th, 75th and 95th percentiles.

## Probability of superiority

Probability-of-superiority is the fraction of all strategy-vs-baseline portfolio pairs where the named strategy scores better on the named metric, with ties counted as one half.

This is **not** the probability that a strategy wins the lottery.

For the exact any-prize benchmark, the underlying metric values are exact, although the set of generator seeds being compared is still a finite sample.

## Bootstrap intervals

For exact any-prize comparisons, the bootstrap resamples **portfolio-generator seed distributions only**. There is no draw-sample uncertainty because every portfolio probability is exact.

For Monte Carlo metrics, the older bootstrap design primarily describes portfolio-seed variability conditional on the shared simulated draw sample. Nested draw+portfolio resampling remains roadmap work only for metrics that still require simulation.

## Browser Benchmark Lab

`benchmark.html` exposes multiple evidence layers:

- a smaller local exploratory multi-seed simulation;
- the generated reference portfolio's exact any-prize probability;
- the Bonferroni lower bound as a separate certified quantity;
- the exact/global-optimal Division-4+ certificate when applicable.

If the static statistics asset predates the exact reference fields, the page reports that a stats refresh is pending rather than inventing values.

## Claim rules

- Never say a bound is exact unless the conditions for exactness have been proved.
- Prefer an exact finite-portfolio probability over a Monte Carlo estimate of the same probability.
- Never infer a Division 1 advantage from lower-order portfolio structure.
- Never report simulated training performance as evidence for a generator.
- Never call probability-of-superiority the probability of winning.
- Do not promote a specialist generator from one small favourable seed sample when a larger confirmation run fails to reproduce a reliable advantage.
- Exact evaluation of a completed portfolio does not by itself prove global optimality over all possible portfolios.
