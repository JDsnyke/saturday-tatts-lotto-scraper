from pathlib import Path


def replace(path: str, old: str, new: str, count: int | None = None) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"missing expected text in {path}: {old[:100]!r}")
    text = text.replace(old, new, -1 if count is None else count)
    target.write_text(text, encoding="utf-8")


def replace_optional(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(old, new), encoding="utf-8")


# Shared Bulma layout fixes: neutral heroes respect both themes, smaller native
# spacing utilities remove excessive whitespace, and section headings are less
# oversized on mobile. No custom CSS is introduced.
for path in ("index.html", "games.html", "benchmark.html"):
    replace(path, 'class="hero-body"', 'class="hero-body py-5"', 1)
    replace(path, 'class="section"', 'class="section py-5"')
    replace(path, 'title is-2 mt-3', 'title is-3 mt-3')
    replace_optional(path, 'notification is-light', 'notification')

replace("index.html", 'class="hero is-primary is-medium"', 'class="hero"')
replace("index.html", 'class="columns is-variable is-8 is-vcentered"', 'class="columns is-vcentered mx-0"', 1)
replace("index.html", 'class="title is-1">Saturday Lotto probability', 'class="title is-2">Saturday Lotto probability', 1)
replace("index.html", 'class="subtitle is-4">Exact odds', 'class="subtitle is-5">Exact odds', 1)
replace(
    "index.html",
    'class="button is-light is-medium" href="#planner"',
    'class="button is-primary is-medium" href="#planner"',
    1,
)
replace(
    "index.html",
    'class="button is-primary is-inverted is-outlined is-medium" href="#tickets"',
    'class="button is-light is-medium" href="#tickets"',
    1,
)
replace("index.html", 'class="title is-2 has-skeleton" id="hero-odds"', 'class="title is-2 is-skeleton" id="hero-odds"', 1)
replace("index.html", '<th>Probability</th><th>Odds</th>', '<th class="is-hidden-mobile">Probability</th><th>Odds</th>', 1)
replace("index.html", 'class="tabs is-boxed"', 'class="tabs is-boxed is-small"', 1)
replace(
    "index.html",
    '<span class="icon"><i data-lucide="bar-chart-3"></i></span><span>Frequency</span>',
    '<span class="icon is-hidden-mobile"><i data-lucide="bar-chart-3"></i></span><span>Frequency</span>',
    1,
)
replace(
    "index.html",
    '<span class="icon"><i data-lucide="waypoints"></i></span><span>Pairs</span>',
    '<span class="icon is-hidden-mobile"><i data-lucide="waypoints"></i></span><span>Pairs</span>',
    1,
)
replace(
    "index.html",
    '<span class="icon"><i data-lucide="shield-check"></i></span><span>Data quality</span>',
    '<span class="icon is-hidden-mobile"><i data-lucide="shield-check"></i></span><span>Quality</span>',
    1,
)
replace(
    "index.html",
    'id="ticket-grid" class="columns is-multiline"',
    'id="ticket-grid" class="columns is-multiline mx-0"',
    1,
)

replace("games.html", 'class="hero is-link is-medium"', 'class="hero"')
replace("games.html", 'class="columns is-vcentered is-variable is-8"', 'class="columns is-vcentered mx-0"', 1)
replace("games.html", 'class="title is-1">Game rules', 'class="title is-2">Game rules', 1)
replace("games.html", 'class="subtitle is-4">Compare current', 'class="subtitle is-5">Compare current', 1)
replace(
    "games.html",
    'class="button is-light is-medium" href="#catalog"',
    'class="button is-link is-medium" href="#catalog"',
    1,
)
replace(
    "games.html",
    'class="button is-link is-inverted is-outlined is-medium" href="#calculators"',
    'class="button is-light is-medium" href="#calculators"',
    1,
)

replace("benchmark.html", 'class="hero is-info is-medium"', 'class="hero"')
replace("benchmark.html", 'class="columns is-vcentered is-variable is-8"', 'class="columns is-vcentered mx-0"', 1)
replace("benchmark.html", 'class="title is-1">Exact results', 'class="title is-2">Exact results', 1)
replace("benchmark.html", 'class="subtitle is-4">Exact portfolio', 'class="subtitle is-5">Exact portfolio', 1)
replace(
    "benchmark.html",
    'class="button is-light is-medium" href="#certificates"',
    'class="button is-info is-medium" href="#certificates"',
    1,
)
replace(
    "benchmark.html",
    'class="button is-info is-inverted is-outlined is-medium" href="#evidence"',
    'class="button is-light is-medium" href="#evidence"',
    1,
)

# Shared theme behaviour: clear both Bulma skeleton variants and keep browser
# chrome metadata aligned with the active Bulma light/dark scheme.
replace(
    "assets/ui.js",
    "root.querySelectorAll('.is-skeleton').forEach(element => element.classList.remove('is-skeleton'));",
    "root.querySelectorAll('.is-skeleton, .has-skeleton').forEach(element => element.classList.remove('is-skeleton', 'has-skeleton'));",
    1,
)
replace(
    "assets/ui.js",
    "localStorage.setItem(THEME_KEY, value);\n\n    const button = document.getElementById('theme-toggle');",
    "localStorage.setItem(THEME_KEY, value);\n\n    const resolved = value === 'system'\n      ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')\n      : value;\n    const themeMeta = document.querySelector('meta[name=\"theme-color\"]');\n    if (themeMeta) themeMeta.content = resolved === 'dark' ? '#14161a' : '#ffffff';\n\n    const button = document.getElementById('theme-toggle');",
    1,
)
replace(
    "assets/ui.js",
    "function setupTheme() {\n    applyTheme(localStorage.getItem(THEME_KEY) || 'system');",
    "function setupTheme() {\n    applyTheme(localStorage.getItem(THEME_KEY) || 'system');\n    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {\n      if ((localStorage.getItem(THEME_KEY) || 'system') === 'system') applyTheme('system');\n    });",
    1,
)

# Dynamic Bulma content: hide wide diagnostic/probability columns on phones and
# reduce ticket-card whitespace with Bulma spacing helpers only.
replace(
    "assets/app.js",
    '<td>${pct(Number(row.probability), 6)}</td><td>${fmtOdds(Number(row.probability))}</td>',
    '<td class="is-hidden-mobile">${pct(Number(row.probability), 6)}</td><td>${fmtOdds(Number(row.probability))}</td>',
    1,
)
replace(
    "assets/app.js",
    '<div class="column is-half">\n      <article class="box">',
    '<div class="column is-half py-2">\n      <article class="box p-4">',
    1,
)
replace(
    "assets/app.js",
    '<th>Number</th><th>Appearances</th><th>Relative count</th><th>z-score</th>',
    '<th>Number</th><th>Appearances</th><th class="is-hidden-mobile">Relative count</th><th>z-score</th>',
    1,
)
replace(
    "assets/app.js",
    '<td><progress class="progress is-primary is-small" value="${row.mainCount || 0}" max="${max}">${row.mainCount || 0}</progress></td><td>${Number(row.zScore || 0).toFixed(2)}</td>',
    '<td class="is-hidden-mobile"><progress class="progress is-primary is-small" value="${row.mainCount || 0}" max="${max}">${row.mainCount || 0}</progress></td><td>${Number(row.zScore || 0).toFixed(2)}</td>',
    1,
)

# Neutral dynamic notifications should follow the Bulma scheme instead of
# forcing a pale surface in dark mode.
for path in ("assets/games.js", "assets/benchmark.js"):
    replace_optional(path, 'notification is-light', 'notification')
