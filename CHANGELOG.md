# Changelog

## 2.1.3 — Exact any-prize portfolio probability

### Added

- exact fixed-portfolio any-prize probability via complement dynamic programming;
- integer counting across all `C(45,6) = 8,145,060` winning-main sets without Monte Carlo enumeration;
- independent one-ticket and two-ticket inclusion-exclusion regression checks;
- default 12-ticket runtime guard so exact evaluation remains an explicit workload;
- `lotto-lab exact-any-prize` CLI command;
- `lotto-lab benchmark-exact-objectives` for seed-matched exact strategy comparisons;
- exact any-prize result in the generated 10-game reference Coverage statistics;
- Benchmark Lab exact-any-prize display above the older Bonferroni bound;
- dedicated exact benchmark workflow and `docs/EXACT_ANY_PRIZE.md`.

### Exact confirmation finding

The larger fixed benchmark uses 32 portfolios for each structured strategy and 128 QuickPick portfolios, all with 10 games and root seed `20260822`.

Mean exact any-prize probabilities:

- Coverage: **23.00372595%**;
- Any-prize-bound: **23.00482171%**;
- Division-4-bound: **23.00703433%**;
- QuickPick: **21.44444742%**.

Coverage vs QuickPick had an exact mean advantage of about **+1.5593 percentage points**, with a portfolio-seed bootstrap 95% interval of about **+1.4769 to +1.6505 points** and probability-of-superiority `1.000` in the fixed benchmark.

Neither specialist bound-driven generator showed a reliable exact any-prize advantage over Coverage in the larger confirmation run. Coverage remains the recommended balanced default.

### Guardrails

- every individual any-prize probability in the exact benchmark is combinatorial, not simulated;
- bootstrap intervals describe generator-seed variation only, not draw-sample uncertainty;
- the smaller 12-seed run that favoured Any-prize-bound is retained in the research history rather than cherry-picked as the release conclusion;
- exact evaluation does not imply global optimisation of the any-prize portfolio;
- equal-size distinct portfolios still have identical Division 1 probability.

## 2.1.2 — Certified portfolio objectives

### Added

- exact two-ticket intersection counts/probabilities for `>=k` main-number events;
- rigorous second-order Bonferroni lower bounds for portfolio union probabilities;
- exact/global-optimality certificates when target ticket events are pairwise disjoint;
- proof-backed Division-4-or-better certificate: max pairwise ticket overlap `<=1` makes `>=4 main` events disjoint;
- `any-prize-bound` ticket mode, which greedily minimises exact pairwise `>=3 main` event-intersection cost;
- `division4-bound` ticket mode, which minimises exact pairwise `>=4 main` intersections and reports when the global optimum is reached;
- `lotto-lab benchmark-objectives` for coverage vs any-prize-bound vs Division-4-bound vs QuickPick;
- probability certificates in ticket metrics and generated reference coverage-set statistics;
- Certified Probability panel in Benchmark Lab;
- tests for exact intersection counts, Bonferroni behaviour and the Division-4 global-optimality theorem.

### Research finding / guardrail

- a prototype that directly trained ticket selection on simulated any-prize outcomes overfit its training draw sample and failed to improve on the existing coverage design out of sample;
- that sampled-training optimiser is not shipped as a recommended strategy;
- a Bonferroni lower bound is never presented as an exact union probability unless disjointness conditions prove exactness;
- Division 1 remains exactly equal for same-sized sets of distinct standard games.

## 2.1.1 — Multi-seed benchmark

### Added

- distribution-vs-distribution benchmarking across independently seeded coverage and QuickPick portfolios;
- shared simulated draw samples for lower-noise strategy comparisons;
- random-baseline 5th/25th/50th/75th/95th percentile summaries;
- bootstrap 95% intervals for favourable mean strategy differences;
- probability-of-superiority effect summaries;
- `lotto-lab benchmark` CLI command;
- reproducible reference benchmark embedded in generated statistics;
- dedicated `benchmark.html` Benchmark Lab with smaller browser-local exploratory runs and JSON export;
- PWA shortcut/offline cache entries for Benchmark Lab;
- benchmark methodology documentation and regression tests.

### Guardrails

- equal-size distinct portfolios remain explicitly equal for Division 1 probability;
- browser-local results are labelled exploratory;
- bootstrap intervals are documented as portfolio-seed uncertainty conditional on the shared simulated draw sample;
- no benchmark result is presented as future-number prediction.

## 2.1.0 — Objective odds & portfolio research

### Added

- exact Division 1 probability across distinct games and repeated draws;
- exact System 6–20 combination equivalence;
- exact 0–6 main-match distribution and Division 1–6 standard-game probabilities;
- pair/triple/quadruple subset coverage metrics;
- combinatorial coverage generator prioritising new quads, triples and pairs;
- actual prize-division Monte Carlo simulation with Wilson 95% intervals;
- leakage-free walk-forward portfolio comparison;
- experimental anti-crowding generator kept separate from draw probability;
- secondary-source verification with draw IDs/source links;
- SHA-256 dataset provenance asset;
- Probability Planner, System calculator, Strategy Evidence and Draw Explorer;
- portfolio CSV/share-link tools and local simulation;
- accessible keyboard frequency-chart details;
- PWA/offline service worker and web manifest;
- static-site integration tests;
- odds-optimisation research note and expanded methodology.

### Changed

- statistics schema advances to v3;
- coverage mode optimises measurable subset diversity rather than number frequency;
- scheduled data refresh can rebuild stale generated assets even if CSV rows do not change;
- data publication is blocked when newest draws fail the independent-source cross-check;
- CI now validates generated provenance, browser JavaScript and static-site references.

### Guardrails

- historical frequency, recency and pair lift remain descriptive only;
- anti-crowding is labelled experimental and cannot be presented as increasing draw probability;
- reference simulations expose sample size/uncertainty and do not claim a universal edge from one seeded baseline.

## 2.0.0 — Probability-first refresh

Replaced the legacy frequency-weighted recommendation system with exact combinatorics, validated Python data tooling, balanced coverage, modern GitHub Pages UI, tests, quieter automation and a living roadmap.
