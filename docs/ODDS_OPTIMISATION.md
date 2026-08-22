# What “improving the odds” can objectively mean

The phrase mixes several different problems. This project keeps them separate.

## 1. Improve Division 1 probability

For a fair 6-from-45 draw, every six-number combination has identical probability.

The only direct ways to increase Division 1 probability are to own more **distinct** combinations or participate in more independent draws. Both also increase exposure/spend.

Choosing hot numbers, cold numbers, overdue numbers, historically common pairs, balanced odd/even patterns or machine-learning recommendations does not change the mathematical probability of the selected combination.

## 2. Improve a fixed-size ticket portfolio

When the number of standard games is fixed, Division 1 probability is fixed too. But the games can be more or less correlated at lower match levels.

Example: two games sharing four numbers reuse the same four-number subset. Two games sharing at most two numbers do not reuse a three- or four-number subset. This changes the distribution of partial matches across the portfolio even though the number of complete six-number combinations is unchanged.

The objective coverage algorithm therefore maximises unique quadruples, triples and pairs and reports the resulting efficiency directly.

This is the strongest currently implemented, mathematically defensible optimisation for a fixed-size multi-game portfolio.

## 3. Improve conditional payout if a winning combination is hit

This is different from winning probability.

If players disproportionately select certain combinations, a winning popular combination can be shared among more winners in a pari-mutuel division. Research in several lottery datasets documents non-uniform human number preferences.

The experimental anti-crowding mode tries to avoid several commonly reported choice features. It should be interpreted only as a hypothesis about **conditional sharing**, not as an increase in the chance of a draw match.

The roadmap requires Australian player-choice calibration before this can become a quantitative payout-sharing model.

## 4. Detect a genuinely biased physical process

In principle, a persistent mechanical or procedural bias could make the fair-draw model wrong. Detecting that would require much stronger evidence than observing hot/cold numbers:

- pre-specified tests;
- controls for multiple comparisons;
- Monte Carlo calibration for dependent draw data;
- persistence across independent time windows;
- ideally physical/procedural corroboration.

Until such evidence exists, the application assumes the documented fair-draw model and treats historical anomalies as audit signals only.

## 5. Compare systems correctly

A System `k` entry is best understood as a convenient representation of `C(k,6)` standard combinations. When comparing options, normalise by the number of distinct standard combinations and by spend rather than treating “System” as a separate source of luck.

## Decision table

| Goal | Objective lever | What does *not* help |
| --- | --- | --- |
| Division 1 in one draw | More distinct six-number combinations | Hot/cold/overdue selection |
| Division 1 over time | More independent exposures | Recency patterns |
| Lower-order portfolio diversity | Fewer repeated pairs/triples/quads | Historical frequency weighting |
| Conditional prize sharing | Potentially less popular human-picked patterns | Claiming those patterns change draw odds |
| Detecting process bias | Pre-specified, calibrated randomness tests | Cherry-picked anomalies |

## Responsible interpretation

Probability improvement from additional games is linear per draw only because more combinations are purchased. Cost rises with it. The software is a research and transparency tool, not a claim that lottery play can be converted into a positive-expectation investment.
