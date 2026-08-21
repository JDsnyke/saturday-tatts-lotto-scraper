# GitHub Pages

The site is a zero-build static dashboard served from the repository root. `deploy.yml` uploads the repository content required by `index.html` and deploys it through the official GitHub Pages actions.

The page reads `assets/lotto_stats.json` at runtime. The weekly `data-refresh.yml` workflow rebuilds this JSON after updating the CSV draw history.

The UI has no framework runtime or package build step, which keeps Pages deployment fast and avoids a JavaScript dependency tree solely for presentation.
