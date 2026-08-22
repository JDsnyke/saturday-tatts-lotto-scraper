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

### Better portfolio construction

- [x] Replace pair-first heuristic with explicit pair/triple/quadruple subset coverage.
- [x] Greedy candidate search prioritising new quads → triples → pairs.
- [x] Report subset placement count, unique count, repeats, efficiency and universe coverage.
- [x] Retain distinct-combination and overlap guarantees.
- [x] Compare optimiser performance against a **distribution** of independently seeded random portfolios.
- [ ] Benchmark greedy search against local search / simulated annealing / integer programming for useful ticket-count ranges.
- [ ] Add objective selector: maximise any-prize probability, ≥4-main coverage, or generic subset diversity.

### Evidence

- [x] Simulate actual prize divisions rather than main matches only.
- [x] Wilson 95% intervals for Monte Carlo hit rates.
- [x] Leakage-free walk-forward historical comparison.
- [x] Surface sample sizes and limitations in UI.
- [x] Bootstrap/repeated-seed confidence interval for strategy **difference** across portfolio seeds.
- [x] Pre-register fixed benchmark seeds/ticket counts in `docs/BENCHMARKING.md`.
- [x] Add probability-of-superiority and random-baseline quantiles.
- [x] Use shared simulated draws across portfolio distributions to reduce comparison noise.
- [ ] Add nested resampling so strategy-difference uncertainty includes both portfolio-seed and draw-sample uncertainty.
- [ ] Add benchmark regression thresholds only after enough releases establish stable expected ranges.

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
- [ ] Add richer accessible SVG charts and comparison views.
- [ ] Add explicit PWA install/update UI.
- [ ] Add Playwright browser smoke tests on a stable CI runner.
- [ ] Compare two saved portfolios side-by-side.
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
- Do **not** claim a strategy advantage from one random seed, one backtest window or overlapping confidence intervals.
- Do **not** call probability-of-superiority the probability that a strategy wins the lottery.
- Do **not** encourage higher spend; probability-vs-spend tools must show both sides of the trade-off.
