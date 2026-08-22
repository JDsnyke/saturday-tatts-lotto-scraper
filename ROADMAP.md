# Saturday Lotto Lab Roadmap

This is the living engineering/research tracker. The governing rule is: **improve measurable probability, coverage, data quality or decision clarity without presenting historical noise as a future-draw edge.**

## v2.0 — Probability-first foundation ✅

- [x] Remove frequency-weighted prediction.
- [x] Add exact `C(45,6) = 8,145,060` Division 1 combinatorics.
- [x] Add distinct QuickPick and balanced multi-entry generation.
- [x] Add strict draw validation and canonical ordering.
- [x] Replace order-sensitive shell statistics with Python diagnostics.
- [x] Add z-scores, entropy, χ² descriptive diagnostic and pair counts.
- [x] Replace the old page with a responsive theme-aware static dashboard.
- [x] Add unit tests, Ruff and CI.
- [x] Remove dependency-PR churn and automated update branches.

## v2.1 — Objective odds & portfolio structure

### Exact probability

- [x] Exact Division 1 probability for any number of distinct standard games.
- [x] Cumulative Division 1 probability across repeated independent draws.
- [x] Exact System 6–20 standard-combination equivalence.
- [x] Exact 0–6 main-number match distribution.
- [x] Exact Division 1–6 standard-game probabilities.
- [x] Exact any-prize probability for a standard game.
- [x] Exact two-ticket intersection probability for any ≥k-main event.
- [x] Rigorous portfolio Bonferroni lower bound `S1 - S2` from exact pair intersections.
- [x] Exact global-optimality certificate when portfolio events are pairwise disjoint.
- [x] Prove that max pairwise game overlap ≤1 makes Division-4-or-better events pairwise disjoint.
- [x] Exact fixed-portfolio any-prize union probability via complement dynamic programming.
- [x] Independent direct/inclusion-exclusion regression checks for the exact DP.
- [x] Embed the exact any-prize result for the generated 10-game reference Coverage portfolio.
- [ ] Improve exact-evaluation scaling beyond the current conservative 12-ticket default cap if a demonstrably efficient state-compression method is found.

### Better portfolio construction

- [x] Replace pair-first heuristic with explicit pair/triple/quadruple subset coverage.
- [x] Greedy candidate search prioritising new quads → triples → pairs.
- [x] Report subset placement count, unique count, repeats, efficiency and universe coverage.
- [x] Retain distinct-combination and overlap guarantees.
- [x] Compare optimiser performance against a **distribution** of independently seeded random portfolios.
- [x] Add an Any-prize-bound objective that minimises exact pair-event intersection cost.
- [x] Add a Division-4-bound objective that can return a global-optimality certificate.
- [x] Keep generic subset-diversity Coverage as a separate objective rather than silently replacing it.
- [x] Evaluate completed portfolios with the exact any-prize union rather than only a second-order bound.
- [ ] **Next priority:** benchmark stronger search methods — local search / simulated annealing / constraint or integer optimisation — using the exact any-prize evaluator as the final objective for practical ticket counts.
- [ ] Explore swap/neighbourhood search starting from Coverage and bound-driven portfolios rather than random restarts only.
- [ ] Investigate symmetry reduction / canonical portfolio representations to avoid evaluating equivalent portfolio structures repeatedly.
- [ ] Determine whether a provable or tightly bounded global optimum is tractable for useful 10-game any-prize portfolios.
- [ ] Determine useful ticket-count ranges where a pairwise-disjoint ≥4-main packing can be constructed reliably.

### Evidence

- [x] Simulate actual prize divisions rather than main matches only.
- [x] Wilson 95% intervals for Monte Carlo hit rates.
- [x] Leakage-free walk-forward historical comparison.
- [x] Surface sample sizes and limitations in UI.
- [x] Bootstrap/repeated-seed confidence interval for strategy **difference** across portfolio seeds.
- [x] Pre-register fixed benchmark seeds/ticket counts in `docs/BENCHMARKING.md`.
- [x] Add probability-of-superiority and random-baseline quantiles.
- [x] Use shared simulated draws across portfolio distributions to reduce comparison noise.
- [x] Add objective benchmark: subset Coverage vs Any-prize-bound vs Division-4-bound vs QuickPick.
- [x] Reject direct simulated-training optimisation after held-out prototypes overfit and failed to improve on Coverage.
- [x] Add exact seed-matched any-prize objective benchmark so the same portfolio families can be evaluated without draw-sample noise.
- [x] Add larger exact confirmation benchmark: 32 seeds per structured strategy vs 128 QuickPick seeds.
- [x] Preserve the smaller favourable 12-seed result while using the larger confirmation run for the release recommendation.
- [x] Confirm a strong exact Coverage-vs-QuickPick any-prize difference in the fixed 10-game benchmark.
- [ ] Add nested resampling where strategy metrics still depend on simulated draw samples; it is unnecessary for exact any-prize probabilities.
- [ ] Add benchmark regression thresholds only after enough exact benchmark releases establish stable expected ranges.

### v2.1.3 exact confirmation finding

10-game portfolios; 32 seeds each for Coverage / Any-prize-bound / Division-4-bound; 128 QuickPick seeds; root seed `20260822`; 320 candidate games per greedy step; 2,000 portfolio-seed bootstrap resamples.

Mean exact any-prize probability:

- Coverage: **23.00372595%**
- Any-prize-bound: **23.00482171%**
- Division-4-bound: **23.00703433%**
- QuickPick: **21.44444742%**

Coverage vs QuickPick:

- exact mean difference: **+1.55927853 percentage points**;
- portfolio-seed bootstrap 95% interval: **+1.47685128 to +1.65048178 points**;
- probability-of-superiority: **1.000** in this fixed benchmark.

Neither specialist structured generator showed a reliable exact any-prize advantage over Coverage in the larger confirmation run. Coverage therefore remains the recommended balanced default.

A smaller 12-seed exact run initially favoured Any-prize-bound. That ordering did not remain convincing when expanded and is retained in the research record rather than used selectively.

Division 1 remains exactly equal for all same-sized sets of distinct standard games.

## v2.1 — Data provenance & auditability

- [x] Secondary-source draw-number and source URL capture.
- [x] SHA-256 checksums for both tracked CSV datasets.
- [x] Secondary verification report.
- [x] Block scheduled publication on newest-draw disagreement.
- [x] Data-health/freshness status in dashboard.
- [x] Saved known-draw parser fixtures.
- [x] Migration-aware regeneration when data assets use an older schema.
- [ ] Prefer an official/regulator machine-readable source if one becomes reliably available.
- [ ] Persist primary source URL/draw ID per historical row rather than only verification metadata for recent draws.

## v2.2 — Conditional prize sharing / crowding research

- [x] Separate conditional payout-sharing logic from draw-probability logic.
- [x] Add an explicitly experimental anti-crowding generator.
- [x] Penalise birthday-heavy, 7, consecutive and highly regular patterns as research-informed features.
- [x] Link the UI and methodology to supporting research.
- [ ] Find or build a defensible Australian Saturday Lotto player-choice dataset.
- [ ] Replace hand-set feature penalties with empirically estimated crowding likelihoods if data supports it.
- [ ] Simulate conditional co-winner/prize-sharing distributions when ticket-popularity data is available.
- [ ] Add expected-value analysis only when prize pool, division rules and player-count inputs are sourced and parameterised.

## v2.3 — Web experience

- [x] Probability Planner.
- [x] System 6–20 calculator.
- [x] Exact prize and main-match views.
- [x] Upgraded portfolio metrics and local simulation.
- [x] Draw search, date filters and number filters.
- [x] Ticket and draw CSV export.
- [x] Shareable ticket URLs using encoded local state only.
- [x] Keyboard-accessible frequency chart details.
- [x] Provenance/data-health UI.
- [x] Offline/PWA caching.
- [x] Static-site integration tests.
- [x] Dedicated Benchmark Lab page with local multi-seed exploratory runs and JSON export.
- [x] PWA shortcut to the Benchmark Lab.
- [x] Certified Probability panel separating exact bounds from Monte Carlo evidence.
- [x] Promote exact reference any-prize probability above the older Bonferroni bound in Benchmark Lab.
- [x] Version the service-worker cache so v2.1.3 evidence UI replaces stale cached v2.1.2 assets.
- [ ] Add richer accessible SVG charts and comparison views.
- [ ] Add explicit PWA install/update UI.
- [ ] Add Playwright browser smoke tests on a stable CI runner.
- [ ] Compare two saved portfolios side-by-side, including exact any-prize comparison when both are within the practical evaluator range.
- [ ] Integrate Benchmark Lab directly into the main navigation after the legacy single-file UI bundle is modularised.

## v2.4 — Formal randomness diagnostics

- [ ] Runs tests for derived binary/count sequences with appropriate calibration.
- [ ] Serial/cross-lag correlation diagnostics.
- [ ] Monte-Carlo-calibrated global goodness-of-fit statistics that respect within-draw dependence.
- [ ] Multiple-testing controls and clear exploratory/confirmatory labelling.
- [ ] Automated alert only for persistent, independently reproduced anomalies — never as a betting signal by default.

## v3 — Reusable lottery research platform

- [ ] Game-definition layer for other Australian lottery formats.
- [ ] Reusable prize-category definitions.
- [ ] Source adapters with provenance contracts.
- [ ] Reproducible research exports/notebooks.
- [ ] Optional fully static precomputed benchmark datasets.

## Permanent guardrails

- Do **not** rank future numbers using hot/cold/due/recency/pair-frequency scores without credible evidence of exploitable non-randomness.
- Do **not** present machine learning as a magic predictor of independent fair draws.
- Do **not** mix anti-crowding / payout-sharing research into the probability of a combination being drawn.
- Do **not** claim a strategy advantage from one random seed, one backtest window or a small favourable benchmark that does not survive a larger confirmation run.
- Do **not** call probability-of-superiority the probability that a strategy wins the lottery.
- Do **not** train an optimiser on simulated draws and report its training performance as evidence; use held-out or exact evaluation and reject it if it fails to generalise.
- Do **not** describe a Bonferroni lower bound as the exact union probability unless the event intersections required for exactness have been proved absent.
- Do **not** equate exact evaluation of a completed portfolio with proof that the portfolio is globally optimal.
- Do **not** encourage higher spend; probability-vs-spend tools must show both sides of the trade-off.
