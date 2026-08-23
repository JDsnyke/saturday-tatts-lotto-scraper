# Australian Lottery Probability Lab Roadmap

This is the living engineering/research tracker. The governing rule is: **improve measurable probability, coverage, data quality or decision clarity without presenting historical noise as a future-draw edge.**

The changelog preserves release-level history; this file focuses on completed capabilities and genuinely open research.

## v2 — Saturday Lotto probability-first foundation ✅

### Probability and data

- [x] Remove frequency-weighted future-number prediction.
- [x] Exact `C(45,6) = 8,145,060` Division 1 combinatorics.
- [x] Exact System-entry equivalence and 0–6 main-match distribution.
- [x] Exact standard-game prize probabilities.
- [x] Strict historical draw validation and canonical ordering.
- [x] Descriptive z-scores, entropy, χ² and pair diagnostics with non-predictive labelling.
- [x] Primary scraper, secondary newest-draw cross-check and SHA-256 provenance.
- [x] Block scheduled publication on secondary-source disagreement.
- [ ] Prefer an official/regulator machine-readable historical source if one becomes reliably available.
- [ ] Persist source URL/draw ID per historical row rather than only recent verification metadata.

### Saturday portfolio probability

- [x] Pair/triple/quadruple Coverage generator.
- [x] Exact two-ticket `>=k` event intersections.
- [x] Bonferroni `S1-S2` union lower bound.
- [x] Prove max ticket overlap `<=1` globally maximises Division-4-or-better union probability for the applicable portfolio size.
- [x] Exact fixed-portfolio any-prize probability via complement dynamic programming.
- [x] Exact multi-seed strategy benchmark.
- [x] Confirm Coverage materially improves exact any-prize union probability versus ordinary QuickPick in the fixed 10-game benchmark while leaving Division 1 unchanged.
- [x] Exact-guided one-swap local search with monotonic exact acceptance.
- [x] Preserve an existing Division-4+ global-optimality certificate during exact-local refinement.
- [x] Freeze exact-local search budget before independent-seed confirmation.
- [ ] Improve exact-evaluation scaling beyond the conservative 12-ticket default if state compression can be demonstrated without weakening exactness.
- [ ] Benchmark larger neighbourhoods / simulated annealing / constraint or integer optimisation against Coverage and exact-local using the exact objective.
- [ ] Investigate symmetry reduction / canonical portfolio representations.
- [ ] Determine whether a provable or tightly bounded global any-prize optimum is tractable for useful 10-game portfolios.

### Saturday evidence guardrails

- [x] Multi-seed portfolio distributions rather than single lucky seeds.
- [x] Shared simulated draws for metrics that remain simulation-based.
- [x] Bootstrap strategy-difference intervals across portfolio seeds.
- [x] Exact mathematics suppresses contradictory Monte Carlo inference when true equality is known.
- [x] Reject simulated-training optimiser after held-out failure.
- [x] Keep Coverage as the fast balanced default; exact-local is optional higher-compute refinement.
- [ ] Add nested resampling only for remaining metrics that genuinely depend on simulated draw samples.
- [ ] Add benchmark regression thresholds only after enough exact releases establish stable ranges.

### Conditional prize-sharing research

- [x] Keep anti-crowding separate from draw probability.
- [x] Experimental penalties for birthday-heavy / regular human-choice patterns.
- [ ] Find or build a defensible Australian player-choice dataset.
- [ ] Replace hand-set crowding penalties with empirically estimated choice likelihoods if data supports them.
- [ ] Model conditional co-winner/prize-sharing distributions only with sourced popularity inputs.

## v3.0 — Reusable Australian lottery research platform ✅ foundation

### Game definitions and exact mechanics

- [x] Operator-aware `GameDefinition`, `PrizePattern` and `SourceRef` layer.
- [x] One-pool combination engine.
- [x] Two-pool Powerball engine.
- [x] Ordered-digit top-prize engine.
- [x] Ordered-without-replacement top-prize engine.
- [x] Exact Keno Spot hypergeometric distribution.
- [x] Cash 3 Any Order multiset-permutation probability.
- [x] Reusable prize patterns kept separate from draw geometry.
- [x] Repeated-draw cumulative probability for Set for Life while retaining per-draw odds separately.

### Current conventional catalog

- [x] Saturday Lotto / TattsLotto.
- [x] Weekday Windfall.
- [x] Oz Lotto.
- [x] Powerball.
- [x] Set for Life.
- [x] Super 66.
- [x] Lotto Strike.
- [x] Lucky Lotteries Super Jackpot.
- [x] Lucky Lotteries Mega Jackpot.
- [x] South Australian Keno through The Lott.
- [x] Instant Scratch-Its as a variable product family.
- [x] Play For Purpose as a variable raffle family.
- [x] Lotterywest Millionaire Medley.
- [x] Lotterywest Cash 3.
- [x] Lotterywest Scratch'n'Win as a variable product family.
- [x] Keep jurisdiction limitations explicit.

### Australian alternative / art-union catalog

- [x] yourtown Prize Home.
- [x] Mater Prize Home current draw snapshot.
- [x] Mater Cars for Cancer current draw snapshot.
- [x] Dream Home Art Union / RSL Queensland snapshot.
- [x] Endeavour Foundation Prize Home snapshot.
- [x] Endeavour Pay Day snapshot.
- [x] Store ticket/entry capacity separately from probability.
- [x] Remove unverified sales-close dates rather than infer them from unrelated terms dates.
- [x] Do not include offshore lottery resellers as Australian alternatives.
- [ ] Add more Australian licensed charity/art-union operators only when current terms and eligibility can be sourced directly.
- [ ] Build automated snapshot expiry/staleness reporting for draw-specific raffle entries.
- [ ] Where operators publish final valid-entry counts, support post-draw exact first-prize denominator calculation with provenance.

### Public source architecture

- [x] Source-stamp definitions with `checked_on` date.
- [x] Publicly mask stale/unreverified aggregate any-prize figures instead of carrying them forward.
- [x] Generate `assets/game_catalog.json` from Python definitions.
- [x] Remove duplicated hard-coded web odds table.
- [x] Dedicated CI workflow regenerates and semantically compares the tracked public catalog.
- [x] Games & Odds Lab consumes the generated catalog.
- [x] PWA caches the generated catalog network-first.
- [ ] Automate periodic operator-rule freshness checks without silently overwriting changed rules.
- [ ] Add source adapters that capture rule revisions / effective dates where operators expose them.

## v3.1 — Game-specific portfolio mathematics

Do not generalise the Saturday optimiser merely because a game has numbered balls. Each objective must match the game's actual winning events.

- [ ] **Oz Lotto:** exact multi-entry union evaluator and Coverage baseline for seven-number tickets.
- [ ] **Set for Life:** exact multi-entry per-draw portfolio union plus clearly separate repeated-seven-draw exposure.
- [ ] **Powerball:** two-pool portfolio model separating main-number overlap from Powerball allocation; determine optimal allocation of secondary-pool choices for fixed game count.
- [ ] **Super 66:** ordered prefix/suffix overlap mathematics across multiple tickets.
- [ ] **Lotto Strike:** ordered-position portfolio overlap and union probability.
- [ ] **Cash 3:** Exact / Any Order portfolio union with duplicate-digit multiset effects.
- [ ] **Keno:** prize-condition models by Spot size and supported jurisdiction/operator before any portfolio optimisation.
- [ ] Establish exact or certified upper/lower bounds before introducing stochastic search for each new game.

## v3.2 — Cross-game decision tools

Cross-game comparison needs more than jackpot odds.

- [ ] Sourced ticket price / standard-entry cost by jurisdiction and product.
- [ ] Sourced prize tables and fixed/pari-mutuel/annuity classification.
- [ ] Jackpot-sharing and rollover semantics.
- [ ] Expected-value calculations only when cost, prize amount, valid prize conditions and sharing/pool inputs are from the same current product/draw.
- [ ] Compare probability per dollar only when entry structure makes the denominator meaningful.
- [ ] Separate annuity face value from present-value assumptions; make discount-rate assumptions explicit.
- [ ] Never rank variable raffles using maximum ticket capacity as though it were final sold/valid entries.

## v3.3 — Web and research experience

- [x] Games & Odds Lab with operator/mechanic/jurisdiction filters.
- [x] Mechanic-specific Set for Life, Keno and Cash 3 calculators.
- [x] Saturday Benchmark Lab and exact certificate UI.
- [x] PWA shortcuts for Games and Benchmark labs.
- [ ] Add game-detail routes generated from catalog data.
- [ ] Side-by-side comparison with evidence labels and jurisdiction warnings.
- [ ] Add explicit catalog freshness/staleness badges per source family.
- [ ] Compare two saved Saturday portfolios side by side.
- [ ] Add Playwright smoke tests on a stable CI runner.
- [ ] Modularise the legacy Saturday single-file browser bundle before deeper navigation integration.

## v4 — Formal diagnostics and reproducible research

- [ ] Runs tests with calibrated null distributions.
- [ ] Serial/cross-lag diagnostics.
- [ ] Monte-Carlo-calibrated global goodness-of-fit tests respecting within-draw dependence.
- [ ] Multiple-testing controls and explicit exploratory/confirmatory labels.
- [ ] Reproducible research exports / notebooks.
- [ ] Optional static benchmark datasets for expensive exact analyses.

## Permanent guardrails

- Do **not** rank future numbers using hot/cold/due/recency/pair-frequency scores without credible evidence of exploitable non-randomness.
- Do **not** present machine learning as a magic predictor of independent fair draws.
- Do **not** mix anti-crowding / payout-sharing research into probability of being drawn.
- Do **not** claim a strategy edge from one seed or small favourable benchmark that fails larger confirmation.
- Do **not** call probability-of-superiority the probability that a strategy wins the lottery.
- Do **not** report optimiser training performance as evidence; use held-out or exact evaluation.
- Do **not** describe a Bonferroni lower bound as an exact union unless required intersections have been proved absent.
- Do **not** equate exact evaluation of a completed portfolio with proof of global optimality.
- Do **not** turn a raffle ticket/entry cap into exact odds unless final valid-entry mechanics justify it.
- Do **not** compare repeated-draw purchases to single draws without labelling the exposure and spend difference.
- Do **not** infer one game's lower-division rules from another game merely because their ball geometry matches.
- Do **not** encourage higher spend; probability-vs-spend tools must show both sides of the trade-off.
