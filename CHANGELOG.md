# Changelog

## 3.0.0 — Australian multi-game foundation

### Added

- operator-aware `GameDefinition`, `PrizePattern` and source-provenance layer for materially different Australian lottery mechanics;
- sourced catalog entries across The Lott, Lotterywest and Australian charity/art-union alternatives;
- exact generic one-pool and two-pool match distributions;
- exact top-prize combinatorics for Saturday/Weekday 6/45, Oz Lotto, Powerball, Set for Life, Super 66, Lotto Strike and Cash 3 Exact Order;
- exact Keno Spot match distribution and Cash 3 Any Order permutation calculation;
- seven-draw cumulative Set for Life probability output while retaining per-draw odds separately;
- `games`, `game-odds`, `game-catalog-json`, `keno` and `cash3` CLI commands routed separately from the mature Saturday command parser;
- Games & Odds Lab static page with operator/mechanic/jurisdiction filters and Set for Life, Keno and Cash 3 calculators;
- sourced alternative snapshots for yourtown Prize Home, Mater Prize Home, Mater Cars for Cancer, Dream Home Art Union, Endeavour Foundation Prize Home and Endeavour Pay Day;
- generated `assets/game_catalog.json` as the single web data source, replacing duplicated odds embedded in JavaScript;
- dedicated Multi-game catalog workflow that regenerates the public catalog and verifies tracked semantic equality;
- `docs/GAME_CATALOG.md` evidence/source taxonomy;
- PWA Games & Odds shortcut and offline catalog caching.

### Probability / provenance rules

- draw mechanics and prize mappings are separate: two games may share the same ball geometry but use different lower-division conditions;
- Powerball is modelled as two independent pools, not a one-pool choose-k game;
- Lotto Strike uses ordered sampling without replacement;
- Super 66 and Cash 3 are ordered-digit games;
- Keno uses hypergeometric Spot mathematics rather than Lotto-combination logic;
- Lucky Lotteries remains raffle-style metadata and is not converted into a fake choose-k model;
- charity/art-union maximum ticket capacity is stored as capacity metadata, **not automatically exact one-ticket odds**;
- scratch-ticket families retain variable print-run/game odds rather than a fabricated universal top-prize denominator;
- public aggregate any-prize figures are masked for Weekday Windfall, Lotto Strike and both Lucky Lotteries products until those aggregate figures are current-source re-verified.

### Source-audit corrections

- removed an unverified Endeavour Pay Day sales-close date rather than confusing a separate terms/eligibility date with ticket sales closure;
- retained Pay Day 221's verified 8 October 2026 draw date, $5 ticket price and 200,000-ticket cap;
- regression-tested Mater Prize Home 327's 13,455,147–22,805,334 possible-entry range rather than collapsing its bundle-dependent entries to a single denominator;
- regression-tested Mater Cars for Cancer 130's 85,117 maximum ticket supply;
- encoded yourtown's explicit rule that First Prize odds depend on tickets actually sold.

### Guardrails

- no historical hot/cold/overdue signal is introduced into any new game;
- an easier jackpot denominator is not described as better expected value;
- repeated-draw exposure such as Set for Life is not compared with a single draw without labelling the difference;
- Saturday-specific portfolio optimisation is not silently applied to Powerball, Oz Lotto, Keno or raffle products;
- offshore lottery resellers are not treated as Australian lottery alternatives.

## 2.1.4 — Exact-guided local portfolio search

### Added

- `exact-local` portfolio mode: start from Coverage, enumerate one-number swaps, screen with exact pair-intersection/Bonferroni structure, then accept only moves that increase the full exact any-prize winning-set count;
- `lotto-lab optimize-any-prize` for an auditable before/after optimisation report;
- paired exact local-search benchmark comparing each refined portfolio with the exact Coverage portfolio it started from;
- explicit preservation of an existing Division-4-or-better global-optimality certificate;
- move history with before/after ticket values and exact winning-set improvement;
- generated `referenceExactLocalSearch` statistics and Benchmark Lab display;
- dedicated holdout workflow using a different root seed from the development benchmark.

### Holdout finding

The release search budget was frozen at **2 passes / 4 bound-ranked exact candidates / 1 exploration candidate** before the independent confirmation run.

On 16 new 10-game Coverage portfolios rooted at seed `20260823`:

- **11/16 improved** and **5/16 were unchanged**;
- no portfolio worsened because acceptance requires a strictly larger exact integer winning-set count;
- mean improvement was **91.75 additional winning-main sets**;
- mean exact any-prize improvement was about **+0.001126 percentage points**;
- paired portfolio-seed bootstrap 95% interval was about **+0.000636 to +0.001664 points**;
- every existing Division-4 global-optimality certificate was preserved;
- Division 1 probability remained unchanged because the number of distinct standard games did not change.

Coverage remains the fast balanced default. `exact-local` is an optional higher-compute refinement for practical smaller portfolios. It is guaranteed non-worse than its own Coverage starting point on the exact any-prize objective, but it is **not** a proof of global optimality.

### Guardrails

- no simulated draw outcomes train or score accepted mutations;
- a cheap Bonferroni score only screens neighbours; the full exact DP decides acceptance;
- development and confirmation seeds are separate;
- the search cannot trade away an existing exact Division-4+ optimum by default;
- local improvement is not described as a future-number prediction or Division 1 edge.

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
