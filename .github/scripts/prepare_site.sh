#!/usr/bin/env bash
set -euo pipefail

rm -rf _site
mkdir -p _site/assets/vendor

cp index.html games.html benchmark.html service-worker.js _site/
cp -R assets/. _site/assets/
cp node_modules/bulma/css/bulma.min.css _site/assets/vendor/bulma.min.css
cp node_modules/lucide/dist/umd/lucide.js _site/assets/vendor/lucide.js
: > _site/.nojekyll

test -s _site/assets/vendor/bulma.min.css
test -s _site/assets/vendor/lucide.js
