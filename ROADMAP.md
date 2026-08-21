# Saturday Lotto Lab Roadmap

This roadmap is the living tracker for the v2 refresh. The guiding rule is simple: improve data quality, transparency and multi-entry coverage without implying that historical results predict an independent lottery draw.

## v2.0 — Probability-first refresh

- [x] Replace frequency-weighted “prediction” with mathematically honest ticket generation.
- [x] Add exact `C(45, 6) = 8,145,060` Division 1 combinatorics.
- [x] Add balanced-coverage ticket generation that reduces repeated number/pair usage across multiple entries.
- [x] Add validated, typed draw parsing with duplicate/range/overlap checks.
- [x] Replace order-sensitive shell statistics with Python diagnostics.
- [x] Add number z-scores, normalized entropy, χ² descriptive diagnostic and historical pair lift.
- [x] Rewrite the GitHub Pages UI with responsive layouts, dynamic charts, animations, accessible tabs and theme switching.
- [x] Add unit tests and Ruff linting.
- [x] Simplify legacy shell scripts into thin compatibility wrappers.
- [x] Remove automated dependency PR churn.
- [x] Replace branch/PR-style updater behaviour with direct, change-only scheduled data commits.
- [x] Refresh project documentation and statistical disclaimers.

## v2.1 — Data provenance & stronger auditability

- [ ] Add draw-number IDs and source URL per draw.
- [ ] Store scrape provenance/checksum metadata alongside each data refresh.
- [ ] Add a second-source comparison job and flag disagreements before committing data.
- [ ] Add a stale-data health badge to the README and website.
- [ ] Add fixture snapshots for known historical draws to catch scraper markup regressions.

## v2.2 — Backtesting & simulation

- [ ] Add walk-forward backtests that compare coverage mode with independent QuickPick baselines.
- [ ] Add Monte Carlo confidence intervals for hit-rate comparisons.
- [ ] Add system-entry coverage comparison (System 7–20) without claiming improved per-combination odds.
- [ ] Add ticket-budget scenarios that show probability versus spend without encouraging higher spend.

## v2.3 — Web experience

- [ ] Add client-side draw search and date filters.
- [ ] Add downloadable JSON/CSV diagnostics.
- [ ] Add shareable ticket-set URLs using encoded local state only.
- [ ] Add richer accessible tooltips and keyboard navigation for charts.
- [ ] Add offline/PWA caching for the static dashboard.

## v3 — Optional research modules

- [ ] Formal randomness diagnostics (runs, serial correlation and Monte Carlo-calibrated goodness-of-fit tests).
- [ ] Player-choice/crowding research only if a defensible Australian dataset becomes available.
- [ ] Conditional prize-sharing simulations clearly separated from draw probability.
- [ ] Support additional Australian lottery formats through a reusable game definition layer.

## Non-goals

- Predicting future winning numbers from “hot”, “cold”, “due”, recency or pair-frequency scores.
- Claiming machine learning can overcome a fair independent lottery draw without evidence of exploitable non-randomness.
- Presenting historical frequency as an individual number’s next-draw probability.
