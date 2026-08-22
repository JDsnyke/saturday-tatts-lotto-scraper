# Exact any-prize portfolio probability

v2.1.3 adds an exact evaluator for the probability that a fixed Saturday Lotto portfolio wins **any** prize.

Under the current six-winning-number prize structure, a standard game wins some division exactly when it matches at least three of the six winning main numbers. Supplementary numbers determine the division within some categories but do not change this binary any-prize event.

## What is computed

For a portfolio of standard six-number games, define `Ai` as the event that ticket `i` matches at least three winning main numbers.

The desired probability is:

```text
P(A1 ∪ A2 ∪ ... ∪ An)
```

There are `C(45,6) = 8,145,060` possible winning-main-number sets. Enumerating every set for every portfolio is unnecessary.

## Complement dynamic programming

The exact algorithm counts the complement:

```text
no-prize event = every ticket finishes with 0, 1 or 2 main-number matches
```

For each ticket, its surviving match count is represented by one base-3 digit:

```text
0 = no selected winning number from this ticket yet
1 = one match
2 = two matches
```

The dynamic-programming state is:

```text
dp[selected_ball_count][base3_match_state] = number of ways to reach that state
```

The 45 balls are processed one at a time. For each ball the algorithm considers not selecting it or selecting it as one of the six winning main numbers. A selecting transition is discarded if it would move any ticket from two matches to three matches, because that state is no longer part of the no-prize complement.

After all 45 balls have been processed:

```text
no_prize_count = sum(dp[6])
any_prize_count = C(45,6) - no_prize_count
exact_probability = any_prize_count / C(45,6)
```

All state weights and favourable-set counts are integers. There is no Monte Carlo sampling and no historical draw input.

## Independent correctness checks

The implementation is regression-tested against results that can be derived without the dynamic program:

- one ticket: direct hypergeometric combinatorics for 3, 4, 5 or 6 main matches;
- two disjoint tickets: exact inclusion-exclusion using the independently tested two-ticket intersection counter;
- two tickets sharing one number: the same independent inclusion-exclusion calculation;
- multi-ticket portfolios: the exact result must lie between the rigorous second-order Bonferroni lower bound and the ordinary union upper bound.

The generated 10-game reference Coverage portfolio is also checked during CI. Its exact result must use all `8,145,060` possible winning-main sets and remain inside the certified bounds.

## Runtime guard

The state space grows with portfolio size and overlap structure. Exact evaluation is therefore deliberately opt-in and capped at **12 tickets by default**.

It is not inserted into every `ticket_metrics()` call. Cheap exact pair-intersection bounds remain suitable for ticket construction and large interactive workloads; the dynamic program is used when an exact fixed-portfolio answer is worth the extra computation.

## Exact objective benchmark

`benchmark-exact-objectives` evaluates Coverage, Any-prize-bound, Division-4-bound and uniform QuickPick portfolios using exact any-prize probabilities.

The deterministic portfolio seeds intentionally match the v2.1.2 simulated objective benchmark. This means exact evaluation can resolve apparent Monte Carlo differences for the same portfolio families rather than changing the experiment after observing the result.

### Larger confirmation benchmark

The v2.1.3 confirmation run uses:

- 10 games per portfolio;
- 32 Coverage portfolios;
- 32 Any-prize-bound portfolios;
- 32 Division-4-bound portfolios;
- 128 QuickPick portfolios;
- root seed `20260822`;
- 320 candidate games per greedy construction step;
- 2,000 bootstrap resamples across portfolio-seed distributions.

Mean **exact** any-prize probabilities were:

| Strategy | Exact mean any-prize probability |
| --- | ---: |
| Coverage | 23.00372595% |
| Any-prize-bound | 23.00482171% |
| Division-4-bound | 23.00703433% |
| QuickPick | 21.44444742% |

### What the comparison supports

Coverage vs QuickPick:

- exact mean difference: **+1.55927853 percentage points**;
- portfolio-seed bootstrap 95% interval: **+1.47685128 to +1.65048178 points**;
- probability-of-superiority: **1.000** in this fixed benchmark — every tested Coverage portfolio had a higher exact any-prize probability than every tested QuickPick portfolio.

This is a portfolio-diversification result. It does not make any six-number combination more likely to be drawn and it does not change Division 1 probability for equal numbers of distinct games.

Any-prize-bound vs Coverage:

- exact mean difference: **+0.00109576 percentage points**;
- portfolio-seed bootstrap 95% interval: **−0.00506409 to +0.00720569 points**;
- probability-of-superiority: **0.4834**.

Division-4-bound vs Coverage on the any-prize objective:

- exact mean difference: **+0.00330837 percentage points**;
- portfolio-seed bootstrap 95% interval: **−0.00168163 to +0.00869012 points**;
- probability-of-superiority: **0.4443**.

Neither specialist generator demonstrates a reliable exact any-prize advantage over Coverage in the larger confirmation distribution. **Coverage therefore remains the recommended balanced default.**

The smaller initial 12-seed exact run had favoured Any-prize-bound, but that ordering did not remain convincing when the exact benchmark was expanded. The project records both results rather than promoting the smaller favourable sample.

## Interpreting the bootstrap interval

Every individual portfolio probability in this benchmark is exact. There is **no draw-sample uncertainty**.

The bootstrap interval describes variation across the sampled deterministic portfolio-generator seeds. It does not prove that one greedy generator is globally optimal over all possible portfolios.

## What remains unsolved

Exact evaluation is not the same as exact optimisation. The project still does not know the globally optimal 10-game portfolio for the any-prize objective.

The next research step is to use the exact evaluator as an out-of-sample / final objective for stronger search methods such as local search, simulated annealing or constraint optimisation, while preserving the existing guardrail that Division 1 probability is determined only by the number of distinct combinations owned.
