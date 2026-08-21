# Changelog

## 2.0.0 — Probability-first refresh

### Changed
- Reframed the project from historical-frequency prediction to transparent lottery research and multi-ticket coverage.
- Replaced the frequency/supplementary weighted recommendation engine with exact 6/45 combinatorics and balanced coverage generation.
- Replaced large shell/awk analysis pipelines with a tested Python package while retaining thin shell compatibility wrappers.
- Rebuilt the GitHub Pages experience with dynamic statistics, responsive layouts, motion, theme switching and a client-side ticket lab.
- Reworked the scheduled data updater so it commits changed data directly instead of creating update branches or pull requests.
- Removed Dependabot PR automation to stop recurring dependency pull-request clutter.
- Removed the stale tag-release workflow until releases can be generated from the new package rather than legacy shell assumptions.

### Added
- Strict draw validation and canonical CSV writing.
- Per-number marginal z-scores, normalized entropy, χ² descriptive distance and historical pair lift.
- Exact multi-ticket Division 1 probability metrics.
- Unit tests and Ruff linting.
- Living `ROADMAP.md` and detailed `docs/METHODOLOGY.md`.

### Fixed
- Date-range calculations no longer depend on CSV append order.
- Current-year scraping is dynamic instead of being capped at 2025.
- Dataset rows are no longer silently skipped because a generator assumes a header is present.

## 1.x

The original bash-based scraper/analyser history predates the v2 architecture. Git history remains the authoritative record for those releases.
