# Changelog

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
